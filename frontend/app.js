const $ = (selector) => document.querySelector(selector);
let selectedResume = null;
let toastTimer;

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
})[character]);

const commaList = (value = "") => value.split(",").map((item) => item.trim()).filter(Boolean);

const toast = (message) => {
    $("#toast").textContent = message;
    $("#toast").classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $("#toast").classList.remove("show"), 4200);
};

async function request(url, options = {}) {
    let response;
    try { response = await fetch(url, options); }
    catch { throw new Error("Unable to reach the backend. Start FastAPI and try again."); }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || data.message || "The request could not be completed.");
    return data;
}

function setButtons(selector, disabled) {
    document.querySelectorAll(selector).forEach((button) => { button.disabled = disabled; });
}

function list(selector, values) {
    $(selector).innerHTML = Array.isArray(values) && values.length
        ? values.map((value) => `<li>${escapeHtml(value)}</li>`).join("")
        : "<li>No information available yet</li>";
}

function renderResumeAnalysis(analysis) {
    const score = Math.max(0, Math.min(100, Number(analysis.resume_score) || 0));
    $("#score-value").textContent = score;
    $("#score-ring").style.background = `conic-gradient(var(--cyan) 0deg, var(--cyan) ${score * 2.35}deg, var(--violet) ${score * 3.6}deg, rgba(255,255,255,.09) ${score * 3.6}deg)`;
    $("#score-summary").textContent = analysis.summary || "Your resume analysis is ready.";
    list("#strengths", analysis.strengths);
    list("#gaps", analysis.missing_skills?.length ? analysis.missing_skills : analysis.weaknesses);
    list("#roles", analysis.recommended_roles);
    $("#resume-detail").classList.remove("hidden");
    $("#resume-detail").innerHTML = `<div><p class="card-label">ATS ACTIONS</p><h3>Make the next application stronger.</h3></div><div class="detail-columns"><div><b>Suggestions</b><ul>${(analysis.ats_suggestions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>No ATS suggestions returned.</li>"}</ul></div><div><b>Project improvements</b><ul>${(analysis.project_improvements || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>No project improvements returned.</li>"}</ul></div></div>`;
}

function selectResume(file) {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) return toast("Please choose a PDF resume.");
    selectedResume = file;
    $("#file-label").textContent = file.name;
    $("#upload-status").textContent = "PDF ready — choose an action below";
    $("#resume-tool-message").textContent = `${file.name} is ready for inspection, analysis, or improvement.`;
    setButtons("[data-resume-action]", false);
}

function resumeFormData() {
    if (!selectedResume) throw new Error("Choose a PDF resume first.");
    const form = new FormData();
    form.append("file", selectedResume);
    return form;
}

async function runResumeAction(action) {
    if (!selectedResume) return toast("Choose a PDF resume first.");
    const button = document.querySelector(`[data-resume-action="${action}"]`);
    const labels = { inspect: "Inspecting PDF…", analyze: "Analyzing resume…", improve: "Improving resume…" };
    button.disabled = true;
    button.textContent = labels[action];
    $("#upload-status").textContent = labels[action];
    try {
        const endpoint = action === "inspect" ? "/resume/upload" : `/resume/${action}`;
        const data = await request(endpoint, { method: "POST", body: resumeFormData() });
        if (action === "inspect") {
            const preview = escapeHtml(data.text || "").slice(0, 6000);
            $("#resume-detail").classList.remove("hidden");
            $("#resume-detail").innerHTML = `<div><p class="card-label">EXTRACTED RESUME TEXT</p><h3>PDF inspection complete.</h3></div><pre>${preview || "No readable text found."}</pre>`;
        } else if (action === "analyze") {
            renderResumeAnalysis(data.analysis);
        } else {
            renderImprovement(data.improved_resume, data.download_url);
        }
        $("#upload-status").textContent = `${action[0].toUpperCase() + action.slice(1)} complete ✦`;
        toast(`${action[0].toUpperCase() + action.slice(1)} completed successfully.`);
    } catch (error) {
        $("#upload-status").textContent = "That action needs another try";
        toast(error.message);
    } finally {
        button.disabled = false;
        button.innerHTML = action === "inspect" ? "Inspect text" : action === "analyze" ? "Analyze resume" : "Improve resume <span>→</span>";
    }
}

function itemText(item) {
    return typeof item === "string" ? item : Object.values(item || {}).filter(Boolean).join(" · ");
}

function renderImprovement(improvement, downloadUrl) {
    const projects = (improvement.projects || []).map((project) => `<li><b>${escapeHtml(project.name)}</b> — ${escapeHtml(project.description)}<br><span>${escapeHtml((project.technologies || []).join(" · "))}</span></li>`).join("") || "<li>No projects found.</li>";
    $("#resume-detail").classList.remove("hidden");
    const download = downloadUrl ? `<a class="download-card" href="${escapeHtml(downloadUrl)}" download>↓ Download your improved resume PDF <span>ATS-ready · PDF</span></a>` : "";
    $("#resume-detail").innerHTML = `<div><p class="card-label">ATS-FRIENDLY RESUME IMPROVEMENT</p><h3>${escapeHtml(improvement.professional_summary || "Your improved resume draft.")}</h3>${download}</div><div class="detail-columns"><div><b>Skills</b><ul>${(improvement.technical_skills || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul><b>Education</b><ul>${(improvement.education || []).map((item) => `<li>${escapeHtml(itemText(item))}</li>`).join("")}</ul></div><div><b>Projects</b><ul>${projects}</ul><b>ATS keywords</b><p class="keyword-line">${(improvement.ats_keywords || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</p></div></div>`;
}

function getProfile() {
    const form = new FormData($("#profile-form"));
    const profile = Object.fromEntries(form.entries());
    profile.skills = commaList(profile.skills);
    profile.interests = commaList(profile.interests);
    return profile;
}

function ensureProfile() {
    const form = $("#profile-form");
    if (!form.reportValidity()) return null;
    return getProfile();
}

function renderRoadmap(career) {
    const roleCards = (career.recommended_roles || []).map((role) => `<div class="role-chip"><b>${escapeHtml(role.role)}</b><span>${escapeHtml(role.match_percentage)}% · ${escapeHtml(role.reason)}</span></div>`).join("");
    const steps = (career.roadmap || []).map((step) => `<div class="roadmap-step"><b>${String(step.month).padStart(2, "0")}</b><p>${escapeHtml(step.focus)}</p></div>`).join("");
    $("#roadmap").innerHTML = `<p class="card-label">PERSONAL ROADMAP</p><h3>Your next six months.</h3><div class="role-stack">${roleCards}</div>${steps}`;
}

async function runCareerAction(action) {
    const profile = ensureProfile();
    if (!profile) return;
    const button = action === "full"
        ? $("#profile-form button[type=submit]")
        : document.querySelector(`[data-career-action="${action}"]`);
    button.disabled = true;
    try {
        if (action === "profile") {
            await request("/career/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
            toast("Career profile validated and ready.");
        } else if (action === "analyze") {
            const data = await request("/career/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
            renderRoadmap(data.analysis);
            toast("Quick career analysis is ready.");
        } else if (action === "recommend") {
            const data = await request("/career/recommend-jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
            $("#job-skills").value = profile.skills.join(", ");
            renderJobs(data.recommended_jobs);
            $("#job-message").textContent = "Recommendations generated from your career profile.";
            toast("Job recommendations are ready.");
        } else {
            const data = await request("/career/career-recommendation", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
            renderRoadmap(data.career_analysis);
            $("#job-skills").value = profile.skills.join(", ");
            renderJobs(data.recommended_jobs);
            $("#job-message").textContent = "Complete AI recommendation generated from your profile.";
            toast(`${data.career_analysis.recommended_roles.length} career directions mapped.`);
        }
    } catch (error) { toast(error.message); }
    finally { button.disabled = false; }
}

function renderJobs(jobs) {
    $("#job-list").innerHTML = Array.isArray(jobs) && jobs.length ? jobs.map((job) => {
        const tags = (job.matched_skills || job.skills || []).map((skill) => `<span class="tag">${escapeHtml(skill)}</span>`).join("") || "<span class=\"tag\">Build your skills</span>";
        const score = job.match_percentage === undefined ? "OPEN" : `${job.match_percentage}% MATCH`;
        return `<article class="job-card glass"><div class="job-top"><p>${escapeHtml(job.company || "Company not listed")} · ${escapeHtml(job.location || "Location not listed")}</p><span class="match">${score}</span></div><h3>${escapeHtml(job.title || "Role not listed")}</h3><p>${escapeHtml(job.salary || "Salary not listed")} · ${escapeHtml(job.experience || "Fresher")}</p><div class="tags">${tags}</div></article>`;
    }).join("") : "<div class=\"glass empty-state\">No matching roles found yet.</div>";
}

async function checkStatus() {
    try { const data = await request("/health"); $("#api-health").textContent = `API ${data.status}`; }
    catch { $("#api-health").textContent = "API offline"; $("#system-strip").classList.add("offline"); }
    try { const data = await request("/career/test"); $("#career-health").textContent = data.status === "success" ? "Career intelligence ready" : "Career service unavailable"; }
    catch { $("#career-health").textContent = "Career service unavailable"; }
}

$("#resume-file").addEventListener("change", (event) => selectResume(event.target.files[0]));
const dropZone = $("#drop-zone");
["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => { event.preventDefault(); dropZone.classList.add("dragging"); }));
["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => { event.preventDefault(); dropZone.classList.remove("dragging"); }));
dropZone.addEventListener("drop", (event) => selectResume(event.dataTransfer.files[0]));
document.querySelectorAll("[data-resume-action]").forEach((button) => button.addEventListener("click", () => runResumeAction(button.dataset.resumeAction)));
document.querySelectorAll("[data-career-action]").forEach((button) => button.addEventListener("click", () => runCareerAction(button.dataset.careerAction)));
$("#profile-form").addEventListener("submit", (event) => { event.preventDefault(); runCareerAction("full"); });
$("#match-jobs").addEventListener("click", async () => {
    const skills = commaList($("#job-skills").value);
    if (!skills.length) return toast("Add at least one skill first.");
    try { const data = await request("/jobs/match", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(skills) }); renderJobs(data.matched_jobs); $("#job-message").textContent = "Skill-match scores updated."; } catch (error) { toast(error.message); }
});
$("#browse-jobs").addEventListener("click", async () => {
    try { const data = await request("/jobs/"); renderJobs(data.jobs); $("#job-message").textContent = "Showing all current sample roles."; } catch (error) { toast(error.message); }
});
checkStatus();
