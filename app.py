import re
from collections import Counter, defaultdict
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

# === Sticky Header ===
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {display: none;}
    footer {visibility: hidden;}

    .sticky-header {
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: white;
        padding: 10px 0;
        z-index: 999;
        border-bottom: 1px solid #ddd;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .sticky-header img {
        height: 32px; /* atur ukuran logo */
    }
    .block-container {padding-top: 80px;}
    </style>
    <div class="sticky-header">
        <img src="https://img.icons8.com/color/48/combo-chart--v1.png" alt="logo">
        <h2 style="margin:0;">Web Log Analyzer</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# === File Upload ===
access_file = st.file_uploader("Upload access.log (optional)", type=["log", "txt"])
error_file = st.file_uploader("Upload error.log (optional)", type=["log", "txt"])
mysql_file = st.file_uploader("Upload mysql-error.log (optional)", type=["log", "txt"])

# === Sidebar ===
st.sidebar.header("⚙️ Pengaturan Tampilan")
days_filter = st.sidebar.number_input("Analisis N hari terakhir", min_value=1, max_value=365, value=7)
show_trend = st.sidebar.checkbox("Tampilkan Tren Error HTTP ≥400 per Jam", value=True)
chart_type = st.sidebar.selectbox("Jenis Grafik", ["Bar", "Line", "Pie"], index=0)


# === Utils ===
def show_chart(df, index_col, chart_type):
    if df.empty: return
    df = df.set_index(index_col)
    if chart_type == "Bar":
        st.bar_chart(df)
    elif chart_type == "Line":
        st.line_chart(df)
    elif chart_type == "Pie":
        fig, ax = plt.subplots()
        df["Count"].plot.pie(ax=ax, autopct="%1.1f%%")
        st.pyplot(fig)


def download_buttons(df, name):
    if df.empty: return
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(f"⬇️ Download CSV ({name})", csv, f"{name}.csv", "text/csv")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=name[:30])
    st.download_button(f"⬇️ Download Excel ({name})", buffer,
        f"{name}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def within_days(date_str, fmt, days):
    try:
        dt = datetime.strptime(date_str, fmt)
        return dt >= datetime.now() - timedelta(days=days)
    except Exception:
        return True


# === ACCESS LOG ===
if access_file:
    access_logs = access_file.read().decode("utf-8", errors="ignore").splitlines()
    access_pattern = re.compile(
        r'(?P<ip>\S+) - - \[(?P<date>.*?)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\S+)'
    )
    status_counter, endpoint_counter, ip_counter = Counter(), Counter(), Counter()
    endpoint_error_counter = Counter()
    time_errors, time_req = defaultdict(int), defaultdict(int)

    for line in access_logs:
        match = access_pattern.search(line)
        if match:
            status = int(match.group("status"))
            path, ip = match.group("path"), match.group("ip")
            date_str = match.group("date").split()[0]
            try:
                dt = datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S")
                if not within_days(dt.strftime("%Y-%m-%d"), "%Y-%m-%d", days_filter):
                    continue
                hour, day = dt.strftime("%Y-%m-%d %H:00"), dt.strftime("%Y-%m-%d")
            except Exception:
                hour, day = "unknown", "unknown"

            status_counter[f"HTTP {status}"] += 1
            endpoint_counter[path] += 1
            ip_counter[ip] += 1
            time_req[hour] += 1
            if status >= 400:
                time_errors[hour] += 1
                endpoint_error_counter[path] += 1

    st.subheader("📈 Statistik Status Code (Semua)")
    df_access = pd.DataFrame(status_counter.items(), columns=["Status Code", "Count"])
    if not df_access.empty:
        st.dataframe(df_access, height=400)
        show_chart(df_access.rename(columns={"Status Code": "Error Code"}), "Error Code", chart_type)
        download_buttons(df_access, "AccessLogStats")

    st.subheader("🌐 Endpoint Paling Sering Diakses")
    df_endpoints = pd.DataFrame(endpoint_counter.most_common(10), columns=["Endpoint", "Hits"])
    if not df_endpoints.empty:
        st.dataframe(df_endpoints, height=400)
        show_chart(df_endpoints.rename(columns={"Hits": "Count"}), "Endpoint", chart_type)
        download_buttons(df_endpoints, "TopEndpoints")

    st.subheader("🚨 Endpoint dengan Error Terbanyak")
    df_ep_err = pd.DataFrame(endpoint_error_counter.most_common(10), columns=["Endpoint", "Errors"])
    if not df_ep_err.empty:
        st.dataframe(df_ep_err, height=400)
        show_chart(df_ep_err.rename(columns={"Errors": "Count"}), "Endpoint", chart_type)
        download_buttons(df_ep_err, "TopErrorEndpoints")

    st.subheader("👤 IP Paling Aktif")
    df_ips = pd.DataFrame(ip_counter.most_common(10), columns=["IP Address", "Hits"])
    if not df_ips.empty:
        st.dataframe(df_ips, height=400)
        show_chart(df_ips.rename(columns={"Hits": "Count"}), "IP Address", chart_type)
        download_buttons(df_ips, "TopIPs")

    if show_trend and time_errors:
        st.subheader("⏱️ Tren Error HTTP ≥400 per Jam")
        df_time = pd.DataFrame(time_errors.items(), columns=["Hour", "Errors"]).sort_values("Hour")
        st.line_chart(df_time.set_index("Hour"))

    if time_req:
        busiest = max(time_req, key=time_req.get)
        st.subheader("🕒 Jam Tersibuk")
        st.write(f"Jam paling sibuk: **{busiest}** dengan **{time_req[busiest]} request**.")

# === APACHE ERROR LOG ===
if error_file:
    error_logs = error_file.read().decode("utf-8", errors="ignore").splitlines()
    error_pattern = re.compile(r'^\[(?P<date>.*?)\] \[(?P<level>\w+):\w+\] .* (?P<message>.*)$')
    error_counter, level_counter, error_time = Counter(), Counter(), defaultdict(int)

    for line in error_logs:
        match = error_pattern.search(line)
        if match:
            level, message = match.group("level").upper(), match.group("message")
            date_str = match.group("date").split()[0]
            try:
                dt = datetime.strptime(date_str.split()[0], "%a %b %d %H:%M:%S.%f %Y")
                if not within_days(dt.strftime("%Y-%m-%d"), "%Y-%m-%d", days_filter):
                    continue
                hour = dt.strftime("%Y-%m-%d %H:00")
            except Exception:
                hour = "unknown"
            key = f"[{level}] {message.split(':')[0]}"
            error_counter[key] += 1
            level_counter[level] += 1
            error_time[hour] += 1

    st.subheader("⚠️ Apache Error Log (Semua Level)")
    df_error = pd.DataFrame(error_counter.items(), columns=["Log Message", "Count"])
    if not df_error.empty:
        st.dataframe(df_error, height=400)
        show_chart(df_error.rename(columns={"Log Message": "Error Message"}), "Error Message", chart_type)
        download_buttons(df_error, "ApacheErrors")

    st.subheader("📊 Distribusi Level Log")
    df_levels = pd.DataFrame(level_counter.items(), columns=["Level", "Count"])
    if not df_levels.empty:
        st.bar_chart(df_levels.set_index("Level"))

    if error_time:
        st.subheader("⏱️ Tren Error Apache per Jam")
        df_err_time = pd.DataFrame(error_time.items(), columns=["Hour", "Count"]).sort_values("Hour")
        st.line_chart(df_err_time.set_index("Hour"))

# === MYSQL ERROR LOG ===
if mysql_file:
    mysql_logs = mysql_file.read().decode("utf-8", errors="ignore").splitlines()
    mysql_error_counter = Counter()
    mysql_pattern = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2}[ T]\S*) \d+ \[(?P<level>\w+)\] (?P<message>.*)$')

    for line in mysql_logs:
        match = mysql_pattern.search(line)
        if match:
            level, message = match.group("level").upper(), match.group("message")
            if level in ("ERROR", "WARNING") or (
                level == "NOTE" and any(kw in message.lower() for kw in ["innodb", "shutdown", "failed", "could not"])
            ):
                key = f"[{level}] {message.split(':')[0]}"
                mysql_error_counter[key] += 1

    st.subheader("🐬 MySQL Error Log")
    df_mysql = pd.DataFrame(mysql_error_counter.items(), columns=["Error Message", "Count"])
    if not df_mysql.empty:
        st.dataframe(df_mysql, height=400)
        show_chart(df_mysql, "Error Message", chart_type)
        download_buttons(df_mysql, "MySQLErrors")

# === INSIGHT ===
st.subheader("🔍 Insight Otomatis")

if access_file and not df_access.empty:
    total_req = len(access_logs)
    total_404 = sum(v for k, v in status_counter.items() if "404" in k)
    total_500 = sum(v for k, v in status_counter.items() if "500" in k)
    total_err = sum(v for k, v in status_counter.items() if int(k.split()[1]) >= 400)
    if total_req > 0:
        error_rate = (total_err / total_req) * 100
        color = "red" if error_rate > 5 else "green"
        st.markdown(f"📊 Total request: **{total_req}**, error: **{total_err}** "
                    f"(Error Rate: <span style='color:{color}'>{error_rate:.2f}%</span>)",
                    unsafe_allow_html=True)
    if total_404 > 0:
        st.write(f"🔍 Ada **{total_404} error 404** → cek broken link / routing.")
    if total_500 > 0:
        st.write(f"🔥 Ada **{total_500} error 500** → periksa bug di aplikasi backend.")

if error_file and 'df_levels' in locals() and not df_levels.empty:
    top_level = df_levels.loc[df_levels["Count"].idxmax()]["Level"]
    st.write(f"⚠️ Apache log level dominan: **{top_level}**.")
    if any("rewrite" in m.lower() for m in df_error["Log Message"]):
        st.write("🔀 Banyak error **mod_rewrite** → periksa konfigurasi .htaccess.")
    if any("timed out" in m.lower() for m in df_error["Log Message"]):
        st.write("⏱️ Ada **script timed out** → optimalkan koding / atur Timeout di Apache.")

if mysql_file and 'df_mysql' in locals() and not df_mysql.empty:
    worst_mysql = df_mysql.loc[df_mysql["Count"].idxmax()]
    st.write(f"🐬 MySQL error dominan: **{worst_mysql['Error Message']}** ({worst_mysql['Count']} kali).")
    if any("innodb" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("💾 Banyak error **InnoDB** → cek tablespace / ibdata1.")
    if any("lock" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("🔒 Masalah **file lock** → pastikan MySQL tidak jalan ganda.")
    if any("collation" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("🔤 Masalah **charset/collation** → cek konfigurasi DB.")
    if any("too many connections" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("📈 **Too many connections** → tingkatkan `max_connections` atau optimalkan pooling.")
    if any("out of memory" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("💥 **Out of memory** → tambah RAM atau optimalkan query.")
    if any("shutdown" in msg.lower() for msg in df_mysql["Error Message"]):
        st.write("🛑 MySQL sering shutdown → cek crash log & konfigurasi.")
