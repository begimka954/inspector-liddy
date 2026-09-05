import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Inspector Liddy",
    page_icon="🕯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clue-style. Crimson, gold, near-black, aged parchment.
# Not a single default Streamlit blue survived this file.
SUSPECT_COLORS = {
    "Lord Blackwood":     "#1e1e6e",
    "Lady Ashford":       "#6e1e6e",
    "Dr. Pembrooke":      "#1e6e1e",
    "Colonel Ravenswood": "#8b1a1a",
    "Miss Thorne":        "#1e6e6e",
    "Graves the Butler":  "#3a3a3a",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&display=swap');

[data-testid="stApp"] {
    background-color: #09060302;
    background-image:
        repeating-linear-gradient(
            0deg, transparent, transparent 27px,
            rgba(58,26,10,0.12) 27px, rgba(58,26,10,0.12) 28px
        ),
        radial-gradient(ellipse at top, #120a04 0%, #060402 100%);
}
[data-testid="stSidebar"] {
    background: #070503;
    border-right: 2px solid #2a1206;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ---- Sidebar dossier header ---- */
.dossier-header {
    background: linear-gradient(135deg, #8b1a1a 0%, #4a0808 100%);
    padding: 22px 18px 16px;
    margin: -1rem -1rem 1.2rem;
    border-bottom: 3px solid #c8960c;
}
.dossier-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.25rem;
    font-weight: 900;
    color: #f4e8c1;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
    line-height: 1.2;
}
.dossier-sub {
    font-size: 0.58rem;
    color: #c89090;
    letter-spacing: 4px;
    text-transform: uppercase;
    font-family: 'Courier New', monospace;
    margin-top: 5px;
}

/* ---- Case file main header ---- */
.case-header {
    border-left: 6px solid #8b1a1a;
    background: linear-gradient(90deg, #0f0804 0%, #07050302 100%);
    padding: 22px 28px 18px;
    margin-bottom: 1.2rem;
    position: relative;
}
.case-eyebrow {
    font-family: 'Courier New', monospace;
    font-size: 0.6rem;
    letter-spacing: 4px;
    color: #5a3010;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.case-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: #f4e8c1;
    letter-spacing: 5px;
    text-transform: uppercase;
    line-height: 1;
    margin: 0;
}
.case-tagline {
    font-family: Georgia, serif;
    font-style: italic;
    font-size: 0.85rem;
    color: #6a4a28;
    margin-top: 8px;
    letter-spacing: 0.5px;
}
.case-stamp {
    position: absolute;
    top: 18px;
    right: 24px;
    border: 2px solid #c8960c;
    color: #c8960c;
    font-size: 0.55rem;
    letter-spacing: 3px;
    padding: 5px 10px;
    font-family: Georgia, serif;
    font-weight: bold;
    text-transform: uppercase;
    transform: rotate(3deg);
    opacity: 0.9;
}
.rule {
    border: none;
    border-top: 1px solid #2a1206;
    margin: 1rem 0 0;
}

/* ---- Deduction trio (prime suspect / weapon / location) ---- */
.deduction-trio {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}
.deduction-card {
    flex: 1;
    border: 1px solid #2a1206;
    border-top: 3px solid #8b1a1a;
    background: #0c0704;
    padding: 10px 12px;
}
.deduction-label {
    font-family: 'Courier New', monospace;
    font-size: 0.55rem;
    letter-spacing: 3px;
    color: #5a3010;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.deduction-value {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 0.92rem;
    color: #f4e8c1;
    font-weight: bold;
    line-height: 1.3;
}

/* ---- Confidence meter ---- */
.meter-label {
    font-family: 'Courier New', monospace;
    font-size: 0.55rem;
    letter-spacing: 3px;
    color: #5a3010;
    text-transform: uppercase;
    margin-bottom: 6px;
}
div[data-testid="stProgress"] > div {
    background: #1a0c04 !important;
    border-radius: 0 !important;
    height: 6px !important;
}
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #8b1a1a, #c8960c) !important;
    border-radius: 0 !important;
}

/* ---- Suspect board cards ---- */
.suspect-card {
    margin-bottom: 7px;
    overflow: hidden;
    border: 1px solid #1e0e04;
}
.suspect-banner { height: 5px; }
.suspect-body {
    background: #0c0704;
    padding: 7px 10px 8px;
}
.suspect-name {
    font-family: Georgia, serif;
    font-size: 0.72rem;
    font-weight: bold;
    color: #d4c090;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.suspect-pct {
    font-family: 'Courier New', monospace;
    font-size: 0.6rem;
    color: #5a3a1a;
    margin-top: 2px;
}
.suspect-bar-bg { background: #1a0c04; height: 3px; margin-top: 5px; }
.suspect-bar-fill { height: 3px; }

/* ---- Section label ---- */
.section-label {
    font-family: 'Courier New', monospace;
    font-size: 0.58rem;
    letter-spacing: 4px;
    color: #5a3010;
    text-transform: uppercase;
    border-bottom: 1px solid #1e0e04;
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* ---- Camera / evidence frame ---- */
.evidence-label {
    font-family: 'Courier New', monospace;
    font-size: 0.58rem;
    letter-spacing: 4px;
    color: #5a3010;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* ---- Inspector narration ---- */
.narration-box {
    border: 1px solid #2a1206;
    border-left: 4px solid #8b1a1a;
    background: #0c0704;
    padding: 14px 16px;
    font-family: Georgia, serif;
    font-style: italic;
    color: #c8a870;
    font-size: 0.88rem;
    line-height: 1.75;
    margin: 10px 0;
}

/* ---- Room detected badge ---- */
.room-badge {
    background: #0c0900;
    border: 1px solid #5a4010;
    border-left: 4px solid #c8960c;
    padding: 8px 14px;
    font-family: Georgia, serif;
    font-size: 0.82rem;
    color: #c8960c;
    margin: 8px 0;
    letter-spacing: 0.5px;
}

/* ---- Notebook (thought log) ---- */
.notebook-wrap {
    background: #f5e9c4;
    background-image: repeating-linear-gradient(
        transparent, transparent 27px, #d8c898 27px, #d8c898 28px
    );
    border: 1px solid #b8a060;
    border-left: 5px solid #8b1a1a;
    padding: 14px 16px 14px 18px;
    font-family: Georgia, serif;
    font-style: italic;
    color: #1e1008;
    font-size: 0.82rem;
    line-height: 28px;
    max-height: 300px;
    overflow-y: auto;
}
.notebook-eyebrow {
    font-family: 'Courier New', monospace;
    font-style: normal;
    font-size: 0.58rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #8b1a1a;
    border-bottom: 1px solid #c8960c;
    padding-bottom: 5px;
    margin-bottom: 8px;
    line-height: 1;
}

/* ---- Buttons ---- */
div[data-testid="stButton"] > button {
    background: #0c0704 !important;
    border: 1px solid #3a1a0a !important;
    color: #c8960c !important;
    font-family: Georgia, serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    padding: 10px 18px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover {
    background: #180e06 !important;
    border-color: #c8960c !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #8b1a1a !important;
    border: 1px solid #c8960c !important;
    color: #f4e8c1 !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #a02020 !important;
}

/* ---- Selectbox ---- */
div[data-testid="stSelectbox"] label {
    color: #5a3010 !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #0c0704 !important;
    border: 1px solid #3a1a0a !important;
    border-radius: 0 !important;
    color: #d4c090 !important;
    font-family: Georgia, serif !important;
}

/* ---- Verdict ---- */
.verdict-wrap {
    padding: 22px 24px;
    border: 1px solid #3a1a0a;
    margin-bottom: 16px;
}
.verdict-correct { border-top: 6px solid #2a6a2a; background: #080e08; }
.verdict-wrong   { border-top: 6px solid #8b1a1a; background: #0e0806; }
.verdict-heading {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.verdict-correct .verdict-heading { color: #5a9a5a; }
.verdict-wrong   .verdict-heading { color: #c84a4a; }
.verdict-line {
    font-family: Georgia, serif;
    font-size: 0.88rem;
    color: #d4c090;
    margin-bottom: 6px;
    line-height: 1.6;
}
.verdict-truth {
    font-family: 'Courier New', monospace;
    font-size: 0.72rem;
    color: #5a3a1a;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid #2a1206;
    letter-spacing: 1px;
}

/* ---- Scrollbars ---- */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #07050302; }
::-webkit-scrollbar-thumb { background: #3a1a0a; }

/* ---- Camera widget ---- */
div[data-testid="stCameraInput"] label {
    color: #5a3010 !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}
div[data-testid="stCameraInput"] > div {
    border: 1px solid #2a1206 !important;
    border-radius: 0 !important;
    background: #080604 !important;
}
</style>
""", unsafe_allow_html=True)


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

    st.session_state.mystery     = m
    st.session_state.session_id  = sid
    st.session_state.liddy       = InspectorLiddy(m, sid)
    st.session_state.detector    = YOLODetector()
    st.session_state.lidar       = LIDARMap()
    st.session_state.game_over   = False
    st.session_state.accusation  = None
    st.session_state.last_cam_id = None


def _suspect_card(name, prob):
    color   = SUSPECT_COLORS.get(name, "#3a3a3a")
    bar_pct = int(prob * 100)
    st.markdown(
        f"<div class='suspect-card'>"
        f"<div class='suspect-banner' style='background:{color};'></div>"
        f"<div class='suspect-body'>"
        f"<div class='suspect-name'>{name}</div>"
        f"<div class='suspect-pct'>{bar_pct}% probability</div>"
        f"<div class='suspect-bar-bg'>"
        f"<div class='suspect-bar-fill' style='width:{bar_pct}%;background:{color};'></div>"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )


def main():
    if "liddy" not in st.session_state:
        _new_game()

    liddy    = st.session_state.liddy
    detector = st.session_state.detector
    lidar    = st.session_state.lidar
    state    = liddy.state()

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown(
            "<div class='dossier-header'>"
            "<div class='dossier-title'>Inspector Liddy</div>"
            "<div class='dossier-sub'>Private Detective &nbsp;|&nbsp; Active Case</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-label'>Current Deduction</div>", unsafe_allow_html=True)

        st.markdown(
            f"<div class='deduction-card' style='margin-bottom:8px;border-top-color:#8b1a1a;'>"
            f"<div class='deduction-label'>Prime Suspect</div>"
            f"<div class='deduction-value'>{state['suspect']}</div></div>"
            f"<div class='deduction-card' style='margin-bottom:8px;border-top-color:#5a3010;'>"
            f"<div class='deduction-label'>Weapon</div>"
            f"<div class='deduction-value'>{state['weapon']}</div></div>"
            f"<div class='deduction-card' style='margin-bottom:14px;border-top-color:#2a5a2a;'>"
            f"<div class='deduction-label'>Location</div>"
            f"<div class='deduction-value'>{state['room']}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='meter-label'>Certainty</div>", unsafe_allow_html=True)
        st.progress(state["confidence"])
        st.markdown(
            f"<p style='font-family:\"Courier New\",monospace;font-size:0.72rem;"
            f"color:#c8960c;margin-top:4px;'>{state['confidence']:.1%}</p>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Suspect Board</div>", unsafe_allow_html=True)

        for name, prob in sorted(state["probs"]["suspects"].items(), key=lambda x: -x[1]):
            _suspect_card(name, prob)

        st.markdown("<br>", unsafe_allow_html=True)

        llm_status = "Narrator active" if state["llm_ready"] else "Templates in use"
        llm_color  = "#2a5a2a" if state["llm_ready"] else "#3a1a0a"
        st.markdown(
            f"<p style='font-family:\"Courier New\",monospace;font-size:0.58rem;"
            f"letter-spacing:2px;color:{llm_color};text-transform:uppercase;'>"
            f"{llm_status}</p>",
            unsafe_allow_html=True,
        )

        if st.button("Open New Case", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ---- Main header ----
    st.markdown(
        "<div class='case-header'>"
        "<div class='case-eyebrow'>Case File &nbsp;|&nbsp; Active Homicide Investigation</div>"
        "<div class='case-title'>Inspector Liddy</div>"
        "<div class='case-tagline'>"
        "The death of Sir Edmund Hartley. One culprit. One weapon. One room. "
        "She has seen worse. She has solved all of them."
        "</div>"
        "<div class='case-stamp'>Active</div>"
        "<hr class='rule'>"
        "</div>",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("<div class='section-label'>Crime Scene Surveillance</div>", unsafe_allow_html=True)

        if not st.session_state.game_over:
            cam_photo = st.camera_input(
                "Aim camera at the scene -- capture when ready",
                key="cam_feed",
            )

            if cam_photo is not None:
                cam_id = id(cam_photo)
                if cam_id != st.session_state.last_cam_id:
                    st.session_state.last_cam_id = cam_id

                    img     = Image.open(cam_photo).convert("RGB")
                    img_arr = np.array(img)

                    detections = detector.detect(img_arr)
                    annotated  = detector.annotate(img_arr, detections)

                    st.image(
                        annotated,
                        caption=f"Evidence Photograph No. {state['scans'] + 1}",
                        use_container_width=True,
                    )

                    lidar.update(detections, img_arr.shape[1], img_arr.shape[0])
                    narration = liddy.scan(detections)

                    st.markdown(
                        f"<div class='narration-box'>{narration}</div>",
                        unsafe_allow_html=True,
                    )

                    from game.world import YOLO_TO_ROOM
                    from collections import Counter
                    detected_labels = [d["class"] for d in detections]
                    detected_rooms  = [YOLO_TO_ROOM[l] for l in detected_labels if l in YOLO_TO_ROOM]
                    if detected_rooms:
                        room_call = Counter(detected_rooms).most_common(1)[0][0]
                        st.markdown(
                            f"<div class='room-badge'>"
                            f"Location identified &nbsp;&mdash;&nbsp; <strong>{room_call}</strong>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    elif detections:
                        st.markdown(
                            f"<div class='room-badge' style='border-left-color:#3a1a0a;color:#5a3a1a;'>"
                            f"Detected: {', '.join(detected_labels)}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<div class='room-badge' style='border-left-color:#3a1a0a;color:#4a2a0a;'>"
                            "Nothing identified. She notes the absence as much as the presence."
                            "</div>",
                            unsafe_allow_html=True,
                        )
        else:
            st.markdown(
                "<div class='narration-box'>The investigation is closed. "
                "Inspector Liddy has made her accusation. She does not revisit conclusions.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Positional LIDAR</div>", unsafe_allow_html=True)
        lidar_img = lidar.render()
        st.image(lidar_img, use_container_width=True)

    with col_right:
        st.markdown("<div class='section-label'>Investigation Controls</div>", unsafe_allow_html=True)

        if not st.session_state.game_over:
            from game.world import SUSPECTS

            if st.button("Forensic Analysis", use_container_width=True):
                note = liddy.run_forensics()
                st.markdown(
                    f"<div class='narration-box'>{note}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            suspect_choice = st.selectbox(
                "Select suspect to interrogate",
                list(SUSPECTS.keys()),
            )
            if st.button("Conduct Interrogation", use_container_width=True):
                note = liddy.interrogate(suspect_choice)
                st.markdown(
                    f"<div class='narration-box'>{note}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Close the Case -- Make Accusation", type="primary", use_container_width=True):
                result = liddy.accuse()
                st.session_state.accusation = result
                st.session_state.game_over  = True
                st.rerun()

        if st.session_state.game_over and st.session_state.accusation:
            res        = st.session_state.accusation
            correct    = res["correct"]
            css_extra  = "verdict-correct" if correct else "verdict-wrong"
            heading    = "Case Closed. Correctly." if correct else "Case Closed. Incorrectly."

            st.markdown(
                f"<div class='verdict-wrap {css_extra}'>"
                f"<div class='verdict-heading'>{heading}</div>"
                f"<div class='verdict-line'>"
                f"<b>{res['suspect']}</b> &nbsp;|&nbsp; "
                f"<b>{res['weapon']}</b> &nbsp;|&nbsp; "
                f"<b>{res['room']}</b>"
                f"</div>"
                f"<div class='verdict-truth'>"
                f"Truth &nbsp;&mdash;&nbsp; "
                f"{res['actual']['culprit']} / {res['actual']['weapon']} / {res['actual']['room']}"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            case_path = liddy.export()
            with open(case_path, "r") as f:
                case_json = f.read()
            st.download_button(
                "Download Case Report",
                case_json,
                file_name="inspector_liddy_case.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Inspector's Notes</div>", unsafe_allow_html=True)

        log_lines = "".join(
            f"<div style='padding-bottom:28px;'>{line}</div>"
            for line in liddy.state()["log"]
        )
        st.markdown(
            f"<div class='notebook-wrap'>"
            f"<div class='notebook-eyebrow'>Liddy's Field Notes</div>"
            f"{log_lines}"
            f"</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
