import streamlit as st
import numpy as np
import threading
import av
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

st.set_page_config(
    page_title="Inspector Liddy",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

SUSPECT_COLORS = {
    "Lord Blackwood":     "#3b82f6",
    "Lady Ashford":       "#a855f7",
    "Dr. Pembrooke":      "#22c55e",
    "Colonel Ravenswood": "#ef4444",
    "Miss Thorne":        "#06b6d4",
    "Graves the Butler":  "#94a3b8",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

[data-testid="stApp"] {
    background: #08080f;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e2e2f0;
}

[data-testid="stSidebar"] {
    background: #0a0a12 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* ---- Status pill with pulse ---- */
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 4px rgba(239,68,68,0); }
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.18);
    border-radius: 999px;
    padding: 4px 12px 4px 8px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #f87171;
}

.pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #ef4444;
    animation: pulse 2s ease-in-out infinite;
}

/* ---- Page header ---- */
.page-header {
    padding: 28px 40px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
}

.header-title {
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -1.5px;
    background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.header-sub {
    font-size: 12px;
    color: #4a4a62;
    font-weight: 400;
    margin-top: 6px;
    letter-spacing: 0.2px;
}

/* ---- Sidebar header ---- */
.sidebar-header {
    padding: 24px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 6px;
}

.sidebar-title {
    font-size: 13px;
    font-weight: 700;
    color: #e2e2f0;
    letter-spacing: -0.3px;
}

.sidebar-eyebrow {
    font-size: 10px;
    color: #3a3a52;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* ---- Deduction strip (top of sidebar) ---- */
.deduction-strip {
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    margin-bottom: 4px;
}

.deduction-item {
    margin-bottom: 14px;
}

.deduction-item:last-child { margin-bottom: 0; }

.d-label {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #3a3a52;
    margin-bottom: 3px;
}

.d-value {
    font-size: 14px;
    font-weight: 600;
    color: #e2e2f0;
    letter-spacing: -0.3px;
}

/* ---- Confidence bar ---- */
.conf-bar-wrap { margin-bottom: 16px; padding: 0 20px; }
.conf-label {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    font-weight: 500;
    color: #3a3a52;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.conf-pct { color: #6b6b8a; font-family: 'JetBrains Mono', monospace; }
.conf-track {
    height: 2px;
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    overflow: hidden;
}
.conf-fill {
    height: 2px;
    border-radius: 999px;
    background: linear-gradient(90deg, #dc2626, #ea580c, #d97706);
}

/* ---- Suspect rows ---- */
.suspect-section {
    padding: 12px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.section-eyebrow {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2a2a3a;
    margin-bottom: 12px;
}

.s-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 8px;
    border-radius: 6px;
    margin-bottom: 2px;
    cursor: default;
    transition: background 0.12s;
}

.s-row:hover { background: rgba(255,255,255,0.03); }

.s-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

.s-name {
    font-size: 12px;
    font-weight: 500;
    color: #c8c8e0;
    flex: 1;
    letter-spacing: -0.2px;
}

.s-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    color: #3a3a52;
}

.s-bar {
    width: 40px;
    height: 2px;
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    overflow: hidden;
}

.s-bar-fill {
    height: 2px;
    border-radius: 999px;
}

/* ---- Main content area ---- */
.main-pad { padding: 28px 40px; }

.section-head {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2e2e44;
    margin-bottom: 14px;
}

/* ---- Glass panel ---- */
.glass {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
}

/* ---- Narration panel ---- */
.narration {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 18px 22px;
    font-family: 'Inter', sans-serif;
    font-size: 13.5px;
    font-style: italic;
    color: #a8a8c0;
    line-height: 1.8;
    margin: 14px 0;
}

/* ---- Room tag ---- */
.room-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(217,119,6,0.07);
    border: 1px solid rgba(217,119,6,0.15);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 500;
    color: #d97706;
    margin: 10px 0;
}

.room-tag-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #d97706;
}

/* ---- Thought log ---- */
.log-panel {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 18px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    color: #3a3a56;
    line-height: 2;
    max-height: 300px;
    overflow-y: auto;
}

.log-line { color: #5a5a78; }
.log-line-active { color: #9090b0; }
.log-prompt { color: #2a2a40; margin-right: 8px; }

/* ---- Verdict ---- */
.verdict {
    border-radius: 12px;
    padding: 24px 26px;
    margin-bottom: 16px;
    border: 1px solid transparent;
}

.verdict-ok {
    background: rgba(34,197,94,0.05);
    border-color: rgba(34,197,94,0.12);
}

.verdict-fail {
    background: rgba(239,68,68,0.05);
    border-color: rgba(239,68,68,0.12);
}

.verdict-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.verdict-ok .verdict-label { color: #22c55e; }
.verdict-fail .verdict-label { color: #ef4444; }

.verdict-main {
    font-size: 16px;
    font-weight: 600;
    color: #e2e2f0;
    letter-spacing: -0.4px;
    line-height: 1.5;
}

.verdict-truth {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #3a3a52;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.05);
}

/* ---- Buttons ---- */
div[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #a0a0c0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px !important;
    border-radius: 8px !important;
    padding: 10px 18px !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}

div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.14) !important;
    color: #e2e2f0 !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #dc2626, #ea580c) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ef4444, #f97316) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(220,38,38,0.25) !important;
}

/* ---- Selectbox ---- */
div[data-testid="stSelectbox"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #2e2e44 !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    color: #c0c0d8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}

/* ---- Camera widget ---- */
div[data-testid="stCameraInput"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #2e2e44 !important;
}

div[data-testid="stCameraInput"] > div {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    background: rgba(0,0,0,0.3) !important;
    overflow: hidden !important;
}

/* ---- Scrollbars ---- */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
}

/* ---- Divider override ---- */
hr { border-color: rgba(255,255,255,0.05) !important; }
</style>
""", unsafe_allow_html=True)


class LiddyProcessor(VideoProcessorBase):
    # She runs continuously. She does not wait for permission.
    def __init__(self):
        self.detector    = None
        self.latest_dets = []
        self.frame_size  = (640, 480)
        self.frame_count = 0
        self._lock       = threading.Lock()

    def recv(self, frame):
        img_bgr = frame.to_ndarray(format="bgr24")
        img_rgb = img_bgr[:, :, ::-1]
        h, w    = img_rgb.shape[:2]

        self.frame_count += 1
        if self.frame_count % 10 == 0 and self.detector is not None:
            dets = self.detector.detect(img_rgb)
            with self._lock:
                self.latest_dets = dets
                self.frame_size  = (w, h)

        with self._lock:
            dets = list(self.latest_dets)

        annotated = self.detector.annotate(img_rgb, dets) if (dets and self.detector) else img_rgb
        return av.VideoFrame.from_ndarray(annotated[:, :, ::-1], format="bgr24")

    def get_latest(self):
        with self._lock:
            return list(self.latest_dets), self.frame_size


def _new_game():
    from game import mystery as mys
    from game import state as st_db
    from inspector.liddy import InspectorLiddy
    from vision.detector import YOLODetector
    from vision.lidar import LIDARMap

    st_db.init()
    m   = mys.generate()
    mys.save(m)
    sid = st_db.start_session(m)

    st.session_state.mystery        = m
    st.session_state.session_id     = sid
    st.session_state.liddy          = InspectorLiddy(m, sid)
    st.session_state.detector       = YOLODetector()
    st.session_state.lidar          = LIDARMap()
    st.session_state.game_over      = False
    st.session_state.accusation     = None
    st.session_state.last_narration = None
    st.session_state.last_dets      = []
    st.session_state.last_room      = None


def _suspect_rows(probs):
    rows = ""
    for name, prob in sorted(probs.items(), key=lambda x: -x[1]):
        color   = SUSPECT_COLORS.get(name, "#64748b")
        pct     = int(prob * 100)
        bar_w   = max(pct, 2)
        rows += (
            f"<div class='s-row'>"
            f"<div class='s-dot' style='background:{color};'></div>"
            f"<div class='s-name'>{name}</div>"
            f"<div class='s-bar'><div class='s-bar-fill' style='width:{bar_w}%;background:{color};'></div></div>"
            f"<div class='s-pct'>{pct}%</div>"
            f"</div>"
        )
    return rows


def main():
    if "liddy" not in st.session_state:
        _new_game()

    liddy    = st.session_state.liddy
    detector = st.session_state.detector
    lidar    = st.session_state.lidar
    state    = liddy.state()
    conf_pct = int(state["confidence"] * 100)

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown(
            "<div class='sidebar-header'>"
            "<div class='sidebar-eyebrow'>Active Investigation</div>"
            "<div class='sidebar-title'>Inspector Liddy</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='deduction-strip'>"
            f"<div class='deduction-item'>"
            f"<div class='d-label'>Prime Suspect</div>"
            f"<div class='d-value'>{state['suspect']}</div>"
            f"</div>"
            f"<div class='deduction-item'>"
            f"<div class='d-label'>Weapon</div>"
            f"<div class='d-value'>{state['weapon']}</div>"
            f"</div>"
            f"<div class='deduction-item'>"
            f"<div class='d-label'>Location</div>"
            f"<div class='d-value'>{state['room']}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='conf-bar-wrap'>"
            f"<div class='conf-label'>"
            f"<span>Certainty</span>"
            f"<span class='conf-pct'>{conf_pct}%</span>"
            f"</div>"
            f"<div class='conf-track'>"
            f"<div class='conf-fill' style='width:{conf_pct}%;'></div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='suspect-section'>"
            f"<div class='section-eyebrow'>Suspects</div>"
            f"{_suspect_rows(state['probs']['suspects'])}"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='padding: 16px 20px;'>", unsafe_allow_html=True)
        if st.button("Open New Case", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Header ----
    case_status = "Closed" if st.session_state.game_over else "Active"
    st.markdown(
        f"<div class='page-header'>"
        f"<div>"
        f"<div class='header-title'>Inspector Liddy</div>"
        f"<div class='header-sub'>The death of Sir Edmund Hartley &nbsp;/&nbsp; Scan {state['scans']} complete</div>"
        f"</div>"
        f"<div class='status-pill'><div class='pulse-dot'></div>{case_status}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ---- Main columns ----
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("<div class='main-pad'>", unsafe_allow_html=True)

        st.markdown("<div class='section-head'>Live Scene Scan</div>", unsafe_allow_html=True)

        ctx = webrtc_streamer(
            key="liddy-cam",
            video_processor_factory=LiddyProcessor,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        if ctx.video_processor:
            ctx.video_processor.detector = detector

        if not st.session_state.game_over:
            if st.button("Scan Current Frame", use_container_width=True):
                dets, (fw, fh) = ctx.video_processor.get_latest() if ctx.video_processor else ([], (640, 480))

                if dets:
                    from game.world import YOLO_TO_ROOM
                    from collections import Counter

                    lidar.update(dets, fw, fh)
                    narration = liddy.scan(dets)
                    st.session_state.last_narration = narration
                    st.session_state.last_dets      = dets

                    rooms = [YOLO_TO_ROOM[d["class"]] for d in dets if d["class"] in YOLO_TO_ROOM]
                    st.session_state.last_room = Counter(rooms).most_common(1)[0][0] if rooms else None
                else:
                    st.session_state.last_narration = "Nothing identified. She waits. Patience is a tool, not a virtue."
                    st.session_state.last_dets = []
                    st.session_state.last_room = None
        else:
            st.markdown(
                "<div class='narration'>Investigation closed. Inspector Liddy has made her accusation. She does not revisit conclusions.</div>",
                unsafe_allow_html=True,
            )

        if st.session_state.get("last_narration"):
            st.markdown(
                f"<div class='narration'>{st.session_state.last_narration}</div>",
                unsafe_allow_html=True,
            )

        if st.session_state.get("last_room"):
            st.markdown(
                f"<div class='room-tag'>"
                f"<div class='room-tag-dot'></div>"
                f"Location confirmed: <strong style='color:#f0c060;'>{st.session_state.last_room}</strong>"
                f"</div>",
                unsafe_allow_html=True,
            )
        elif st.session_state.get("last_dets"):
            labels = [d["class"] for d in st.session_state.last_dets]
            st.markdown(
                f"<div class='room-tag' style='color:#6b6b8a;border-color:rgba(107,107,138,0.15);background:rgba(107,107,138,0.04);'>"
                f"<div class='room-tag-dot' style='background:#6b6b8a;'></div>"
                f"Detected: {', '.join(labels)}"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-head'>Positional LIDAR</div>", unsafe_allow_html=True)
        lidar_img = lidar.render()
        st.image(lidar_img, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='main-pad'>", unsafe_allow_html=True)

        if not st.session_state.game_over:
            from game.world import SUSPECTS

            st.markdown("<div class='section-head'>Actions</div>", unsafe_allow_html=True)

            if st.button("Forensic Analysis", use_container_width=True):
                note = liddy.run_forensics()
                st.markdown(f"<div class='narration'>{note}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            suspect_choice = st.selectbox("Interrogate suspect", list(SUSPECTS.keys()))
            if st.button("Conduct Interrogation", use_container_width=True):
                note = liddy.interrogate(suspect_choice)
                st.markdown(f"<div class='narration'>{note}</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Close the Case", type="primary", use_container_width=True):
                result = liddy.accuse()
                st.session_state.accusation = result
                st.session_state.game_over  = True
                st.rerun()

        if st.session_state.game_over and st.session_state.accusation:
            res     = st.session_state.accusation
            correct = res["correct"]
            cls     = "verdict-ok" if correct else "verdict-fail"
            label   = "Correct" if correct else "Incorrect"

            st.markdown(
                f"<div class='verdict {cls}'>"
                f"<div class='verdict-label'>{label}</div>"
                f"<div class='verdict-main'>"
                f"{res['suspect']}<br>"
                f"<span style='color:#6b6b8a;font-size:13px;font-weight:400;'>"
                f"{res['weapon']} / {res['room']}"
                f"</span></div>"
                f"<div class='verdict-truth'>"
                f"Truth: {res['actual']['culprit']} / {res['actual']['weapon']} / {res['actual']['room']}"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            case_path = liddy.export()
            with open(case_path, "r") as f:
                case_json = f.read()
            st.download_button(
                "Download Case Report",
                case_json,
                file_name="case_report.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-head'>Inspector's Notes</div>", unsafe_allow_html=True)

        log_lines = "".join(
            f"<div class='log-line'><span class='log-prompt'>&gt;</span>{line}</div>"
            for line in liddy.state()["log"]
        )
        st.markdown(
            f"<div class='log-panel'>{log_lines}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
