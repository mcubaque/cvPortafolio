"""
Generate ATS-optimized CV PDFs for Marco Cubaque.
Compatible with fpdf2 >= 2.7  — uses explicit set_xy() + _space_check() guard
so that captured `y` is never stale after an auto-page-break.
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

C_DARK   = (30,  41,  59)
C_ACCENT = (29,  78,  216)
C_TEXT   = (51,  65,  85)
C_MUTED  = (100, 116, 139)
C_RULE   = (226, 232, 240)

LH = 5.0   # standard line height (mm)


class CV(FPDF):
    FONT = "Helvetica"

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=15)
        self.BW = self.w - self.l_margin - self.r_margin  # 174 mm

    def _f(self, style="", size=10):
        self.set_font(self.FONT, style, size)

    def _c(self, rgb):
        self.set_text_color(*rgb)

    def _goto(self, x_off=0):
        self.set_x(self.l_margin + x_off)

    def _nl(self, h=3):
        self.ln(h)

    def _space_check(self, needed=None):
        """Add a page if less than `needed` mm remains before the auto-break margin.
        Call this BEFORE capturing get_y() so the captured Y is never stale."""
        if needed is None:
            needed = LH
        if self.get_y() + needed > self.h - self.b_margin:
            self.add_page()

    def hr(self, thickness=0.2):
        y = self.get_y()
        self.set_draw_color(*C_RULE)
        self.set_line_width(thickness)
        self.line(self.l_margin, y, self.l_margin + self.BW, y)
        self.ln(2)

    # ── Name / contact block ────────────────────────────────────────────────
    def name_block(self, name, tagline, contacts):
        self._f("B", 20);  self._c(C_DARK)
        self.cell(self.BW, 9, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._f("", 11);   self._c(C_ACCENT)
        self.cell(self.BW, 6, tagline, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._nl(2);  self.hr()
        self._f("", 8.2);  self._c(C_MUTED)
        self.cell(self.BW, 5, "   ".join(contacts),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._nl(1);  self.hr()

    # ── Section header ──────────────────────────────────────────────────────
    def section(self, title):
        self._nl(4)
        self._f("B", 9);   self._c((255, 255, 255))
        self.set_fill_color(*C_DARK)
        self.cell(self.BW, 6.5, "  " + title, fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._c(C_TEXT);  self._nl(2)

    # ── Two-column row (label | value) ──────────────────────────────────────
    def two_col(self, label, value, w_lbl=58, bold_lbl=True, size=9.5):
        self._space_check(LH)          # guard: capture y only after space confirmed
        w_val = self.BW - w_lbl
        y = self.get_y()

        self._f("B" if bold_lbl else "", size);  self._c(C_DARK)
        self.set_xy(self.l_margin, y)
        self.multi_cell(w_lbl, LH, label)
        y_after_lbl = self.get_y()

        self._f("", size);  self._c(C_TEXT)
        self.set_xy(self.l_margin + w_lbl, y)
        self.multi_cell(w_val, LH, value)
        y_after_val = self.get_y()

        self.set_y(max(y_after_lbl, y_after_val))

    # ── Bullet line ─────────────────────────────────────────────────────────
    def bullet(self, text, indent=5, size=9.5):
        self._space_check(LH)          # guard: dash cell won't trigger page break
        w_dash = 4
        w_text = self.BW - indent - w_dash
        y = self.get_y()

        self._f("", size);  self._c(C_TEXT)
        self.set_xy(self.l_margin + indent, y)
        self.cell(w_dash, LH, "-")
        self.set_xy(self.l_margin + indent + w_dash, y)
        self.multi_cell(w_text, LH, text)

    # ── Job entry ───────────────────────────────────────────────────────────
    def job(self, title, company, date_str, stack, bullets):
        self._space_check(16)          # keep title+company+first stack line together
        W_DATE  = 52
        W_TITLE = self.BW - W_DATE
        y = self.get_y()

        self._f("B", 10);  self._c(C_DARK)
        self.set_xy(self.l_margin, y)
        self.cell(W_TITLE, 5.5, title)

        self._f("", 8.5);  self._c(C_MUTED)
        self.set_xy(self.l_margin + W_TITLE, y)
        self.cell(W_DATE, 5.5, date_str, align="R")
        self.set_y(y + 5.5)

        self._f("B", 9);  self._c(C_ACCENT)
        self._goto()
        self.cell(self.BW, 4.5, company, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if stack:
            self._f("", 8);  self._c(C_MUTED)
            self._goto()
            self.multi_cell(self.BW, 4, "Stack: " + stack)
        self._nl(1.5)

        for b in bullets:
            self.bullet(b)
        self._nl(2)

    # ── Education entry ─────────────────────────────────────────────────────
    def edu(self, degree, institution, years):
        self._space_check(10)
        W_YR  = 30
        W_DEG = self.BW - W_YR
        y = self.get_y()

        self._f("B", 10);  self._c(C_DARK)
        self.set_xy(self.l_margin, y)
        self.cell(W_DEG, 5.5, degree)

        self._f("", 8.5);  self._c(C_MUTED)
        self.set_xy(self.l_margin + W_DEG, y)
        self.cell(W_YR, 5.5, years, align="R")
        self.set_y(y + 5.5)

        self._f("", 9);  self._c(C_ACCENT)
        self._goto()
        self.cell(self.BW, 4.5, institution, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._nl(2)

    # ── Certification entry ─────────────────────────────────────────────────
    def cert(self, name, issuer_year):
        self._space_check(LH)
        W_ISS  = 52
        W_NAME = self.BW - W_ISS
        y = self.get_y()

        self._f("", 9.5);  self._c(C_TEXT)
        self.set_xy(self.l_margin + 3, y)
        self.cell(4, LH, "-")

        self._f("B", 9.5)
        self.set_xy(self.l_margin + 7, y)
        self.cell(W_NAME - 7, LH, name)

        self._f("", 8.5);  self._c(C_MUTED)
        self.set_xy(self.l_margin + W_NAME, y)
        self.cell(W_ISS, LH, issuer_year, align="R")
        self.set_y(y + LH)

    # ── Plain paragraph ─────────────────────────────────────────────────────
    def para(self, text, size=9.5):
        self._f("", size);  self._c(C_TEXT)
        self._goto()
        self.multi_cell(self.BW, LH + 0.3, text)
        self._nl(2)


# ═══════════════════════════════════════════════════════════════════════════
#  ENGLISH VERSION
# ═══════════════════════════════════════════════════════════════════════════
def build_en():
    cv = CV()
    cv.add_page()

    cv.name_block(
        "Marco Cubaque",
        "Software Engineer  |  Database Administrator",
        ["mcubaque@gmail.com", "+57 319 685 0846", "Bogota, Colombia",
         "linkedin.com/in/marcocubaque", "github.com/mcubaque"],
    )

    cv.section("CAREER PROFILE")
    cv.para(
        "Software Engineer and Database Administrator with 5+ years of experience designing, "
        "optimizing, and migrating enterprise data environments. Specialist in SQL Server, MySQL, "
        "and PostgreSQL, with strong focus on high availability, performance tuning, and backend "
        "development with Python and Flask."
    )
    cv.para(
        "Currently at AGS Colombia, leading full-stack development of internal enterprise platforms "
        "- including an AI-powered recruitment system (OpenAI/Groq) and a project management tool "
        "with Kanban, sprints, and time tracking - combining deep DBA expertise with application "
        "development. Previous experience includes building PostgreSQL HA clusters with Patroni, "
        "HAProxy, and Docker at RithmXO (Lindon UT, remote). "
        "Open to relocation and international opportunities."
    )

    cv.section("SKILLS")
    cv.two_col("Programming & Backend:", "Python, Flask, FastAPI, JavaScript")
    cv.two_col("Databases:",             "SQL Server (T-SQL), PostgreSQL, MySQL")
    cv.two_col("Infrastructure:",        "Docker, Patroni, HAProxy, Git, Linux")
    cv.two_col("AI & APIs:",             "OpenAI API, Groq API, GLPI API")
    cv.two_col("Frontend:",              "Bootstrap 5, HTML, CSS, Chart.js")
    cv.two_col("Methodologies:",         "Scrum / Agile  (SFC Certified)")

    cv.section("EXPERIENCE")

    cv.job(
        title="Database Administrator & Software Developer",
        company="AGS Colombia SAS",
        date_str="October 2025 - Present",
        stack="Python, Flask, SQL Server, MySQL, PostgreSQL, Bootstrap 5, OpenAI/Groq API, GLPI API, Chart.js, openpyxl, fpdf2",
        bullets=[
            "Full-stack development of enterprise internal applications for medical audit, HR, and project management.",
            "Built GestionRH: full-cycle recruitment platform with 7-stage pipeline, AI-powered CV parsing (OpenAI/Groq), candidate compatibility scoring 0-100%, and automated email notifications.",
            "Built HU Tracker: internal project management tool with Kanban board, sprint planning, time tracking (Clockify-style), task dependency graph (DAG), and GLPI ticketing integration.",
            "Designed and optimized relational schemas in SQL Server, MySQL, and PostgreSQL for mission-critical corporate applications.",
            "Collaborated with Technology, HR, and Finance teams in requirements gathering, technical design, and production deployments.",
        ],
    )
    cv.job(
        title="Database Administrator Engineer",
        company="RithmXO - Lindon, UT (Remote)",
        date_str="March 2024 - September 2025",
        stack="SQL Server, MySQL, PostgreSQL, Python, Docker, Patroni, HAProxy, Linux",
        bullets=[
            "Administration and optimization of SQL Server and PostgreSQL instances across Linux and Windows environments.",
            "Led migration of MSSQL databases to PostgreSQL, reducing licensing costs and improving scalability.",
            "Designed and deployed a PostgreSQL HA cluster using Docker, Patroni, and HAProxy - achieving automatic failover and load balancing.",
            "Implemented proactive monitoring and alerting systems, preventing critical production incidents.",
            "Optimized queries and indexes, significantly reducing execution times on high-traffic workloads.",
            "Standardized data modeling criteria and documented stress-test procedures across all environments.",
        ],
    )
    cv.job(
        title="Database Administrator",
        company="Atica - Industria Ambiental",
        date_str="November 2021 - April 2023",
        stack="SQL Server, MySQL, Python, Power BI, Excel",
        bullets=[
            "Design and administration of network and database infrastructure.",
            "Relational data modeling and logical structure design.",
            "Development of dynamic reports and dashboards (Power BI).",
            "Implementation and control of the information security management system.",
            "Designed comprehensive security policies; led data management solution improving accessibility, efficiency, and regulatory compliance.",
        ],
    )
    cv.job(
        title="Database Administrator & Web Developer",
        company="SyT Comunicaciones",
        date_str="June 2020 - June 2021",
        stack="PHP, MySQL, WordPress, Git, HTML, CSS, Bootstrap",
        bullets=[
            "Design and development of web applications and computer systems.",
            "Service and database query optimization; instance monitoring and incident response.",
            "Developed customer management system with centralized data, automated alerts, and personalized notifications.",
        ],
    )

    cv.section("EDUCATION")
    cv.edu("Software Engineering (B.Sc.)",
           "Politecnico Grancolombiano - Bogota, Colombia", "2021 - 2023")
    cv.edu("Systems Analysis & Development (A.S.)",
           "SENA - Manizales, Colombia", "2017 - 2020")

    cv.section("CERTIFICATIONS")
    cv.cert("Scrum Fundamentals Certified (SFC)", "SCRUMstudy  |  2022")
    cv.cert("Database Administrator",             "Carlos Slim Foundation  |  2020")
    cv.cert("Data Curator",                       "Carlos Slim Foundation  |  2020")

    cv.section("LANGUAGES")
    cv.two_col("Spanish:", "Native")
    cv.two_col("English:", "Intermediate (B1)")

    out = os.path.join(OUT_DIR, "MarcoResumeEng.pdf")
    cv.output(out)
    print(f"Generated: {out}  ({cv.page} pages)")


# ═══════════════════════════════════════════════════════════════════════════
#  SPANISH VERSION
# ═══════════════════════════════════════════════════════════════════════════
def build_es():
    cv = CV()
    cv.add_page()

    cv.name_block(
        "Marco Cubaque",
        "Ingeniero de Software  |  Administrador de Bases de Datos",
        ["mcubaque@gmail.com", "+57 319 685 0846", "Bogota, Colombia",
         "linkedin.com/in/marcocubaque", "github.com/mcubaque"],
    )

    cv.section("PERFIL PROFESIONAL")
    cv.para(
        "Ingeniero de Software y Administrador de Bases de Datos con mas de 5 anos de experiencia "
        "disenando, optimizando y migrando entornos de datos empresariales. Especialista en "
        "SQL Server, MySQL y PostgreSQL, con enfoque solido en alta disponibilidad, optimizacion "
        "de rendimiento y desarrollo backend con Python y Flask."
    )
    cv.para(
        "Actualmente en AGS Colombia, liderando el desarrollo full-stack de plataformas empresariales "
        "internas - incluyendo un sistema de reclutamiento con IA (OpenAI/Groq) y una herramienta "
        "de gestion de proyectos con Kanban, sprints y time tracking - combinando profundidad en DBA "
        "con desarrollo de aplicaciones. Experiencia previa construyendo clusters PostgreSQL de alta "
        "disponibilidad con Patroni, HAProxy y Docker en RithmXO (Lindon UT, remoto). "
        "Disponible para reubicacion y oportunidades internacionales."
    )

    cv.section("HABILIDADES")
    cv.two_col("Programacion & Backend:", "Python, Flask, FastAPI, JavaScript")
    cv.two_col("Bases de Datos:",         "SQL Server (T-SQL), PostgreSQL, MySQL")
    cv.two_col("Infraestructura:",        "Docker, Patroni, HAProxy, Git, Linux")
    cv.two_col("IA & APIs:",              "OpenAI API, Groq API, GLPI API")
    cv.two_col("Frontend:",               "Bootstrap 5, HTML, CSS, Chart.js")
    cv.two_col("Metodologias:",           "Scrum / Agile  (SFC Certificado)")

    cv.section("EXPERIENCIA")

    cv.job(
        title="Administrador de BD & Desarrollador de Software",
        company="AGS Colombia SAS",
        date_str="Octubre 2025 - Actualidad",
        stack="Python, Flask, SQL Server, MySQL, PostgreSQL, Bootstrap 5, OpenAI/Groq API, GLPI API, Chart.js, openpyxl, fpdf2",
        bullets=[
            "Desarrollo full-stack de aplicaciones internas para auditoria medica, gestion humana y gestion de proyectos.",
            "Desarrolle GestionRH: plataforma con pipeline de 7 etapas, parser de CVs con IA (OpenAI/Groq), score de compatibilidad 0-100% y notificaciones automaticas por email.",
            "Desarrolle HU Tracker: herramienta con tablero Kanban, sprints, time tracking estilo Clockify, grafo de dependencias (DAG) e integracion GLPI.",
            "Disene y optimice esquemas relacionales en SQL Server, MySQL y PostgreSQL para aplicaciones de mision critica.",
            "Colabore con equipos de Tecnologia, RRHH y Finanzas en levantamiento de requerimientos y puesta en produccion.",
        ],
    )
    cv.job(
        title="Ingeniero Administrador de Bases de Datos",
        company="RithmXO - Lindon, UT (Remoto)",
        date_str="Marzo 2024 - Septiembre 2025",
        stack="SQL Server, MySQL, PostgreSQL, Python, Docker, Patroni, HAProxy, Linux",
        bullets=[
            "Administracion y optimizacion de instancias SQL Server y PostgreSQL en entornos Linux y Windows.",
            "Lidere migracion de bases de datos MSSQL a PostgreSQL, reduciendo costos de licenciamiento.",
            "Disene y desplegue cluster HA PostgreSQL con Docker, Patroni y HAProxy - failover automatico y balanceo de carga.",
            "Implemente sistemas de monitoreo proactivo y alertas, previniendo incidentes criticos en produccion.",
            "Optimice consultas e indices, reduciendo tiempos de ejecucion en cargas de trabajo de alto trafico.",
            "Estandarice criterios de modelado y documente procedimientos de pruebas de estres.",
        ],
    )
    cv.job(
        title="Administrador de Bases de Datos",
        company="Atica - Industria Ambiental",
        date_str="Noviembre 2021 - Abril 2023",
        stack="SQL Server, MySQL, Python, Power BI, Excel",
        bullets=[
            "Diseno y administracion de infraestructura de red y bases de datos.",
            "Modelado relacional y diseno de estructura logica de datos.",
            "Desarrollo de reportes dinamicos y dashboards (Power BI).",
            "Implementacion y control del sistema de gestion y seguridad de la informacion.",
            "Disene politicas integrales de seguridad; lidere solucion mejorando accesibilidad, eficiencia y cumplimiento normativo.",
        ],
    )
    cv.job(
        title="Administrador de BD & Desarrollador Web",
        company="SyT Comunicaciones",
        date_str="Junio 2020 - Junio 2021",
        stack="PHP, MySQL, WordPress, Git, HTML, CSS, Bootstrap",
        bullets=[
            "Diseno y desarrollo de aplicaciones web y sistemas informaticos.",
            "Optimizacion de servicios y consultas; monitoreo de instancias y respuesta a incidentes.",
            "Desarrolle sistema de gestion de clientes con alertas automaticas y notificaciones personalizadas.",
        ],
    )

    cv.section("EDUCACION")
    cv.edu("Ingenieria de Software",
           "Politecnico Grancolombiano - Bogota, Colombia", "2021 - 2023")
    cv.edu("Analisis y Desarrollo de Sistemas (Tecnologo)",
           "SENA - Manizales, Colombia", "2017 - 2020")

    cv.section("CERTIFICACIONES")
    cv.cert("Scrum Fundamentals Certified (SFC)", "SCRUMstudy  |  2022")
    cv.cert("Administrador de Bases de Datos",    "Fundacion Carlos Slim  |  2020")
    cv.cert("Curador de Datos",                   "Fundacion Carlos Slim  |  2020")

    cv.section("IDIOMAS")
    cv.two_col("Espanol:", "Nativo")
    cv.two_col("Ingles:",  "Intermedio (B1)")

    out = os.path.join(OUT_DIR, "MarcoResume.pdf")
    cv.output(out)
    print(f"Generated: {out}  ({cv.page} pages)")


if __name__ == "__main__":
    build_en()
    build_es()
    print("Done.")
