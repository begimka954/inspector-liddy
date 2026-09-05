import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Inspector Liddy",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inline CSS because a separate file is overkill for a murder investigation
st.markdown("""
<style>
[data-testid="stApp"] { background-color: #13100c; }
[data-testid="stSidebar"] { background-color: #0d0b08; }
.block-container { padding-top: 1.5rem; }
.log-box {
    background: #0a0806;
    border: 1px solid #3a2e1e;
    border-radius: 4px;
    padding: 14px 16px;
    font-family: "Courier New", monospace;
    color: #c8a96e;
    max-height: 280px;
    overflow-y: auto;
    font-size: 0.82rem;
    line-height: 1.6;
}
.card {
    background: #0d0b08;
    border: 1px solid #3a2e1e;
    border-radius: 5px;
    padding: 12px;
    text-align: center;
    margin-bottom: 8px;
}
.card-label { color: #c8a96e; font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase; }
.card-value { color: #f0e8d4; font-size: 1.05rem; font-weight: bold; margin-top: 4px; }
.verdict-correct { background:#1f3d1f; border:1px solid #3a6b3a; border-radius:6px; padding:20px; }
.verdict-wrong   { background:#3d1f1f; border:1px solid #6b3a3a; border-radius:6px; padding:20px; }
</style>
""", unsafe_allow_html=True)


def _new_game():
    from game import mystery as mys
    from game import state as st_db
    from inspector.liddy import InspectorLiddy
    from vision.detector import YOLODetector
    from vision.lidar import LIDARMap

    st_db.init()
    m = mys.generate()
    mys.save(m)
    sid = st_db.start_session(m)

    st.session_state.mystery     = m
    st.session_state.session_id  = sid
    st.session_state.liddy       = InspectorLiddy(m, sid)
    st.session_state.detector    = YOLODetector()
    st.session_state.lidar       = LIDARMap()
    st.session_state.game_over   = False
    st.session_state.accusation  = None
    st.session_state.last_cam_id = None   # tracks camera widget state


def _card(label, value):
    st.markdown(
        f"<div class='card'>"
        f"<div class='card-label'>{label}</div>"
        f"<div class='card-value'>{value}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def main():
    if "liddy" not in st.session_state:
        _new_game()

    liddy    = st.session_state.liddy
    detector = st.session_state.detector
    lidar    = st.session_state.lidar

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(
            "<h2 style='color:#c8a96e;font-family:Georgia;'>Inspector Liddy</h2>"
            "<p style='color:#7a6a50;font-size:0.8rem;'>Her mind is methodical enough to frighten.</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        state = liddy.state()
        _card("Prime Suspect", state["suspect"])
        _card("Likely Weapon", state["weapon"])
        _card("Location",      state["room"])
        # Room comes from YOLO. Your couch just told Inspector Liddy where she is.

        st.markdown(f"<p style='color:#7a6a50;font-size:0.8rem;'>Confidence</p>", unsafe_allow_html=True)
        st.progress(state["confidence"])
        st.markdown(f"<p style='color:#c8a96e;'>{state['confidence']:.1%}</p>", unsafe_allow_html=True)

        st.divider()

        # Suspect probability breakdown
        st.markdown("<p style='color:#7a6a50;font-size:0.75rem;letter-spacing:1px;'>SUSPECT BOARD</p>", unsafe_allow_html=True)
        for name, prob in sorted(state["probs"]["suspects"].items(), key=lambda x: -x[1]):
            bar_pct = int(prob * 100)
            st.markdown(
                f"<div style='margin-bottom:6px;'>"
                f"<span style='color:#c8a96e;font-size:0.75rem;'>{name}</span>"
                f"<div style='background:#1e1a14;border-radius:3px;height:6px;margin-top:3px;'>"
                f"<div style='background:#c8a96e;width:{bar_pct}%;height:6px;border-radius:3px;'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

        if state["llm_ready"]:
            st.markdown("<p style='color:#3a6b3a;font-size:0.7rem;'>LLM narrator active</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#6b3a3a;font-size:0.7rem;'>LLM offline, templates in use</p>", unsafe_allow_html=True)

        st.divider()
        if st.button("New Case", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # --- Main area ---
    st.markdown(
        "<h1 style='color:#c8a96e;font-family:Georgia;letter-spacing:3px;margin-bottom:0;'>INSPECTOR LIDDY</h1>"
        "<p style='color:#5a4a30;font-family:Georgia;margin-top:4px;'>"
        "The death of Sir Edmund Hartley. One culprit. One weapon. One room.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Scan the Scene")

        if not st.session_state.game_over:
            cam_photo = st.camera_input(
                "Point the camera at your crime scene, then capture",
                key="cam_feed",
            )

            if cam_photo is not None:
                # Only process a new capture -- Streamlit reruns on every interaction
                cam_id = id(cam_photo)
                if cam_id != st.session_state.last_cam_id:
                    st.session_state.last_cam_id = cam_id

                    img     = Image.open(cam_photo).convert("RGB")
                    img_arr = np.array(img)

                    detections = detector.detect(img_arr)
                    annotated  = detector.annotate(img_arr, detections)

                    st.image(annotated, caption=f"Scan #{state['scans'] + 1}", use_container_width=True)

                    lidar.update(detections, img_arr.shape[1], img_arr.shape[0])
                    narration = liddy.scan(detections)

                    st.markdown(
                        f"<div class='log-box'><i>{narration}</i></div>",
                        unsafe_allow_html=True,
                    )

                    # Tell the player which room Inspector Liddy thinks she is in
                    from game.world import YOLO_TO_ROOM
                    detected_labels = [d["class"] for d in detections]
                    detected_rooms  = [YOLO_TO_ROOM[l] for l in detected_labels if l in YOLO_TO_ROOM]
                    if detected_rooms:
                        from collections import Counter
                        room_call = Counter(detected_rooms).most_common(1)[0][0]
                        st.info(f"Inspector Liddy has placed herself in: **{room_call}**")
                    elif detections:
                        st.caption(f"Detected: {', '.join(detected_labels)}")
                    else:
                        st.caption("Nothing recognised in this frame. She scans again without comment.")
        else:
            st.info("The investigation is closed. Inspector Liddy has made her accusation.")

        # LIDAR
        st.markdown("### LIDAR Positional Map")
        lidar_img = lidar.render()
        st.image(lidar_img, use_container_width=True)

    with col_right:
        st.markdown("### Inspector's Actions")

        if not st.session_state.game_over:
            from game.world import SUSPECTS

            if st.button("Run Forensics", use_container_width=True):
                note = liddy.run_forensics()
                st.success(note)

            st.markdown("---")
            suspect_choice = st.selectbox(
                "Select a suspect to interrogate",
                list(SUSPECTS.keys()),
            )
            if st.button("Interrogate", use_container_width=True):
                note = liddy.interrogate(suspect_choice)
                st.warning(note)

            st.markdown("---")
            if st.button("Make Final Accusation", type="primary", use_container_width=True):
                result = liddy.accuse()
                st.session_state.accusation = result
                st.session_state.game_over  = True
                st.rerun()

        # Accusation reveal
        if st.session_state.game_over and st.session_state.accusation:
            res = st.session_state.accusation
            css_class = "verdict-correct" if res["correct"] else "verdict-wrong"
            verdict    = "Correct. As expected." if res["correct"] else "Wrong. That is unexpected."

            st.markdown(
                f"<div class='{css_class}'>"
                f"<h3 style='color:#f0e8d4;'>{verdict}</h3>"
                f"<p style='color:#d0c8b0;'>My accusation: <b>{res['suspect']}</b>"
                f" with the <b>{res['weapon']}</b>"
                f" in the <b>{res['room']}</b></p>"
                f"<hr style='border-color:#444;'>"
                f"<p style='color:#a09080;font-size:0.9rem;'>The truth: "
                f"{res['actual']['culprit']} / {res['actual']['weapon']} / {res['actual']['room']}</p>"
                f"</div>",
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

        # Thought log
        st.markdown("### Thought Log")
        current_log = liddy.state()["log"]
        log_html = "<br><br>".join(f"-- {line}" for line in current_log)
        st.markdown(f"<div class='log-box'>{log_html}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
