import streamlit as st
import os
import pandas as pd
from resume_parser import extract_text_from_pdf, clean_text, extract_top_skills

from job_matching import calculate_similarity

# ------------------ PAGE TITLE ------------------
st.set_page_config(page_title="AI Resume Screening System")
st.title("🤖 AI Resume Screening System")

# ------------------ INPUTS ------------------
job_text = st.text_area("Paste Job Description Here")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF)",
    type="pdf",
    accept_multiple_files=True
)

# ------------------ MAIN BUTTON ------------------
if st.button("Rank Resumes"):

    results = []

    if job_text and uploaded_files:

        job_text = clean_text(job_text)

        # ----------- PROCESS EACH RESUME -----------
        for uploaded_file in uploaded_files:
            try:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                resume_text = extract_text_from_pdf(uploaded_file.name)
                resume_text = clean_text(resume_text)
                skills = extract_top_skills(resume_text, top_n=5)

                score = calculate_similarity(job_text, resume_text)
                results.append((uploaded_file.name, score, ", ".join(skills)))

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        # ----------- SORT RESULTS -----------
        if results:
            results = sorted(results, key=lambda x: x[1], reverse=True)

            results_df = pd.DataFrame(results, columns=["Filename", "Score", "Skills"])

            # --------- DISPLAY TABLE ----------
            st.subheader("📊 Ranked Resumes")
            st.dataframe(results_df, use_container_width=True)

            # ---------- PROGRESS BARS ----------
            st.subheader("📊 Match Visualization")
            for filename, score,skills in results:
                st.write(f"**{filename}**")
                st.progress(min(int(score), 100))

            # ---------- BEST MATCH ----------
            top_resume, top_score, top_skills = results[0]
            st.success(f"⭐ Best Match: {top_resume} ({top_score:.2f}%)")

            # ---------- DOWNLOAD ----------
            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Download Results CSV",
                data=csv,
                file_name="resume_ranking.csv",
                mime="text/csv",
            )

        else:
            st.warning("No results generated.")

    else:
        st.warning("⚠️ Please provide job description and upload resumes.")
