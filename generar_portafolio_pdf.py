from fpdf import FPDF


class PortfolioPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(0, 150, 136)
            self.cell(0, 8, "LlanoPay | Portafolio de Startup", align="R")
            self.ln(4)
            self.set_draw_color(0, 150, 136)
            self.set_line_width(0.4)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(0, 120, 110)
        self.cell(0, 14, title)
        self.ln(10)
        self.set_draw_color(0, 150, 136)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title)
        self.ln(9)

    def body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6.5, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(60, 60, 60)
        self.cell(6, 6.5, "-")
        self.multi_cell(0, 6.5, text)
        self.ln(1)

    def highlight_box(self, text):
        self.set_fill_color(240, 248, 247)
        self.set_draw_color(0, 150, 136)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 100, 90)
        y = self.get_y()
        self.rect(10, y, 190, 14, style="DF")
        self.set_xy(15, y + 3)
        self.cell(0, 8, text)
        self.ln(18)

    def stat_box(self, label, value):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(0, 120, 110)
        self.cell(60, 12, value, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 150, 136)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 8, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        if fill:
            self.set_fill_color(240, 248, 247)
        else:
            self.set_fill_color(255, 255, 255)
        max_h = 6
        for i, col in enumerate(cols):
            lines = self.multi_cell(widths[i], 6, col, border=0, dry_run=True, output="LINES")
            h = len(lines) * 6
            if h > max_h:
                max_h = h
        x_start = self.get_x()
        y_start = self.get_y()
        for i, col in enumerate(cols):
            self.set_xy(x_start + sum(widths[:i]), y_start)
            self.multi_cell(widths[i], 6, col, border=1, fill=fill, new_x="RIGHT", new_y="TOP")
        self.set_y(y_start + max_h)


def generate():
    pdf = PortfolioPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ==================== PORTADA ====================
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 42)
    pdf.set_text_color(0, 120, 110)
    pdf.cell(0, 18, "LLANOPAY", align="C")
    pdf.ln(20)
    pdf.set_draw_color(0, 150, 136)
    pdf.set_line_width(1.5)
    pdf.line(55, pdf.get_y(), 155, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "La billetera digital de los Llanos Orientales", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Inclusion financiera para la region con mayor", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "potencial de crecimiento en Colombia", align="C")
    pdf.ln(25)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Portafolio de Startup", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Abril 2026", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Documento Confidencial", align="C")

    # ==================== EL PROBLEMA ====================
    pdf.add_page()
    pdf.section_title("El Problema")

    pdf.body(
        "Los Llanos Orientales de Colombia (Meta, Casanare, Arauca, Vichada, Guainia, "
        "Guaviare) representan el 30% del territorio nacional, pero sus habitantes "
        "enfrentan una severa exclusion financiera:"
    )
    pdf.ln(3)

    pdf.sub_title("Brechas Identificadas")
    pdf.bullet("El 45% de la poblacion rural de los Llanos no tiene cuenta bancaria")
    pdf.bullet("Solo el 23% de los municipios cuentan con sucursal bancaria fisica")
    pdf.bullet("Las transferencias entre personas dependen de efectivo o giros costosos (3-5% de comision)")
    pdf.bullet("Los comercios locales no tienen acceso a pagos digitales accesibles")
    pdf.bullet("Los ganaderos, agricultores y petroleros manejan grandes sumas en efectivo, con alto riesgo")
    pdf.bullet("No existe una solucion financiera disenada para la realidad de la region")
    pdf.bullet("Las remesas desde Venezuela son costosas y lentas por canales formales")

    pdf.ln(5)
    pdf.highlight_box("  Mercado desatendido: 2.5 millones de personas en 6 departamentos")

    # ==================== LA SOLUCION ====================
    pdf.add_page()
    pdf.section_title("La Solucion")

    pdf.body(
        "LlanoPay es una billetera digital disenada especificamente para los Llanos "
        "Orientales de Colombia. Permite enviar, recibir y administrar dinero desde "
        "el celular, con o sin conexion bancaria tradicional."
    )
    pdf.ln(3)

    pdf.sub_title("Funcionalidades Principales")

    features = [
        ["Billetera Digital", "Cuenta digital en pesos colombianos (COP) accesible desde cualquier "
         "celular. Carga de saldo via PSE, Nequi, Daviplata, tarjetas o efectivo en "
         "puntos autorizados (Efecty, Baloto). Sin costos de mantenimiento."],
        ["Transferencias P2P", "Envio de dinero persona a persona por numero de celular. "
         "Comisiones desde 0.5% (hasta 10x mas barato que giros tradicionales). "
         "Transferencias instantaneas 24/7. Limites configurables."],
        ["Marketplace Regional", "Directorio de comercios locales que aceptan LlanoPay. "
         "Pagos con codigo QR. Sistema de calificaciones y resenas. "
         "Promociones y descuentos exclusivos."],
        ["Microcredito", "Prestamos pequenos para emprendedores y trabajadores de la region. "
         "Score crediticio basado en historial de uso de la app. "
         "Montos desde $50,000 hasta $5,000,000 COP. Tasas competitivas."],
        ["Llanocoin (LLO)", "Token digital regional que funciona como programa de lealtad "
         "y medio de intercambio dentro del ecosistema. Recompensas por uso, "
         "descuentos en comercios, acceso a beneficios exclusivos."],
        ["Criptomonedas", "Compra, venta y custodia de criptomonedas (Bitcoin, Ethereum, USDT). "
         "Ideal para remesas internacionales y ahorro en moneda estable. "
         "Conversion directa COP a cripto y viceversa."],
    ]
    w = [35, 145]
    pdf.table_header(["Modulo", "Descripcion"], w)
    for i, row in enumerate(features):
        pdf.table_row(row, w, fill=(i % 2 == 0))

    # ==================== PROPUESTA DE VALOR ====================
    pdf.add_page()
    pdf.section_title("Propuesta de Valor")

    pdf.sub_title("Para Usuarios")
    pdf.bullet("Abrir cuenta en 2 minutos, solo con numero de celular")
    pdf.bullet("Enviar dinero a cualquier persona por $500 COP (vs $5,000-15,000 de giros)")
    pdf.bullet("Cargar saldo sin necesidad de cuenta bancaria (efectivo en Efecty/Baloto)")
    pdf.bullet("Acceso a credito basado en comportamiento, no en historial bancario")
    pdf.bullet("Ahorro en criptomonedas estables (USDC) para protegerse de la inflacion")
    pdf.bullet("Funciona en zonas con conectividad limitada (modo offline basico)")

    pdf.ln(5)
    pdf.sub_title("Para Comercios")
    pdf.bullet("Recibir pagos digitales sin terminal POS ni cuota mensual")
    pdf.bullet("Visibilidad en el marketplace regional (miles de usuarios potenciales)")
    pdf.bullet("Liquidacion de pagos en 24 horas a cuenta bancaria o billetera")
    pdf.bullet("Herramientas de promociones y fidelizacion de clientes")
    pdf.bullet("Dashboard con analitica de ventas y clientes")

    pdf.ln(5)
    pdf.sub_title("Para la Region")
    pdf.bullet("Formalizacion de la economia: transacciones trazables y seguras")
    pdf.bullet("Reduccion del uso de efectivo y los riesgos asociados")
    pdf.bullet("Estimulo al comercio local y la economia circular regional")
    pdf.bullet("Inclusion financiera de poblaciones historicamente excluidas")
    pdf.bullet("Canal para remesas Venezuela-Colombia a bajo costo")

    # ==================== MODELO DE NEGOCIO ====================
    pdf.add_page()
    pdf.section_title("Modelo de Negocio")

    pdf.body(
        "LlanoPay genera ingresos a traves de multiples fuentes, lo que diversifica "
        "el riesgo y maximiza el valor por usuario:"
    )
    pdf.ln(3)

    modelo = [
        ["Comisiones por transferencia", "0.5% a 1.5% por transferencia P2P segun monto. "
         "Transferencias menores a $100,000: 0.5%. Entre $100,000 y $1,000,000: 1.0%. "
         "Mayores a $1,000,000: 1.5%. Ingreso recurrente por volumen de transacciones."],
        ["Comisiones a comercios", "1.5% a 2.5% por cada pago recibido via LlanoPay. "
         "Menor que las comisiones de tarjetas de credito (3-4%). "
         "Planes premium con comision reducida."],
        ["Spread cambiario cripto", "0.5% a 1.0% de spread en compra/venta de criptomonedas. "
         "Ingreso por cada conversion COP a cripto y viceversa. "
         "Volumen creciente con adopcion cripto en la region."],
        ["Intereses de microcredito", "Tasa de interes del 1.5% al 3% mensual sobre prestamos. "
         "Cartera diversificada en montos pequenos (bajo riesgo individual). "
         "Score crediticio propio reduce morosidad."],
        ["Llanocoin (LLO)", "Comision del 1% en compra/venta del token. "
         "Reserva de valor del token genera interes por tenencia. "
         "Alianzas con comercios que aceptan LLO con descuento."],
        ["Servicios Premium", "Cuenta premium sin comisiones por $15,000/mes. "
         "Retiros ilimitados, prioridad en soporte, limites mas altos. "
         "Seguro de transacciones."],
    ]
    w_mod = [42, 138]
    pdf.table_header(["Fuente de Ingreso", "Detalle"], w_mod)
    for i, row in enumerate(modelo):
        pdf.table_row(row, w_mod, fill=(i % 2 == 0))

    # ==================== MERCADO ====================
    pdf.add_page()
    pdf.section_title("Tamano del Mercado")

    pdf.sub_title("TAM (Mercado Total Direccionable)")
    pdf.body(
        "Billeteras digitales en Colombia: $4.2 billones COP en transacciones anuales (2025). "
        "Crecimiento del 35% anual. 25 millones de usuarios potenciales a nivel nacional."
    )

    pdf.sub_title("SAM (Mercado Disponible)")
    pdf.body(
        "Poblacion de los Llanos Orientales: 2.5 millones de personas. "
        "Penetracion de smartphones: 72%. Poblacion bancarizada: 55%. "
        "Mercado disponible: 1.8 millones de usuarios potenciales con smartphone."
    )

    pdf.sub_title("SOM (Mercado Objetivo Inicial)")
    pdf.body(
        "Meta inicial: Villavicencio y municipios aledanos (Meta). "
        "Poblacion objetivo: 600,000 personas. "
        "Meta de captura en 18 meses: 50,000 usuarios activos (8.3% penetracion)."
    )

    pdf.ln(3)
    pdf.highlight_box("  Oportunidad: Sin competidor directo enfocado en los Llanos Orientales")

    pdf.ln(3)
    pdf.sub_title("Competencia")
    comp = [
        ["Nequi", "Nacional", "Gratuita, amplia adopcion", "No enfocada en regiones rurales, sin cripto, sin marketplace local"],
        ["Daviplata", "Nacional", "Vinculada a Davivienda, efectivo en cajeros", "Sin enfoque regional, sin microcredito basado en app"],
        ["Movii", "Nacional", "Para no bancarizados", "Funcionalidad limitada, sin cripto ni marketplace"],
        ["Rappipay", "Nacional", "Ecosistema Rappi", "Solo urbano, dependiente de Rappi, sin enfoque regional"],
        ["LlanoPay", "Regional", "Disenada para los Llanos, cripto, microcredito, marketplace, token regional", "Marca nueva, requiere traccion inicial"],
    ]
    w_comp = [25, 20, 55, 80]
    pdf.table_header(["Nombre", "Alcance", "Fortaleza", "Debilidad"], w_comp)
    for i, row in enumerate(comp):
        pdf.table_row(row, w_comp, fill=(i % 2 == 0))

    # ==================== MANEJO DE DINERO ====================
    pdf.add_page()
    pdf.section_title("Manejo de Dinero Real")

    pdf.body(
        "LlanoPay opera con dinero real a traves de alianzas con proveedores financieros "
        "regulados en Colombia. La plataforma nunca toca el dinero directamente, sino que "
        "actua como orquestador de servicios financieros."
    )
    pdf.ln(3)

    pdf.sub_title("Entrada y Salida de Pesos Colombianos (COP)")
    fiat = [
        ["Pasarela de pagos principal", "Procesamiento de pagos via PSE (transferencia bancaria), "
         "tarjetas de credito/debito, y billeteras como Nequi y Daviplata. "
         "Proveedores: Wompi, PayU o ePayco."],
        ["Pagos en efectivo", "Los usuarios pueden cargar saldo en puntos fisicos como Efecty, "
         "Baloto y redes SuRed. Reciben un codigo en la app, pagan en la tienda, "
         "y el saldo se acredita automaticamente."],
        ["Retiros a cuenta bancaria", "Dispersion de fondos a cualquier cuenta bancaria colombiana "
         "en 24 horas habiles. Tambien retiro a Nequi o Daviplata."],
    ]
    w_fiat = [48, 132]
    pdf.table_header(["Canal", "Como Funciona"], w_fiat)
    for i, row in enumerate(fiat):
        pdf.table_row(row, w_fiat, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Criptomonedas y Activos Digitales")
    crypto = [
        ["Exchange regulado", "Alianza con exchange autorizado (Bitso, Binance) para "
         "compra/venta de criptomonedas. El usuario compra BTC, ETH o USDT "
         "directamente desde la app."],
        ["Stablecoins (USDC)", "Integracion con emisor de stablecoins para pagos internacionales "
         "y remesas. El USDC esta respaldado 1:1 por dolares americanos. "
         "Proveedor: Circle."],
        ["Custodia segura", "Las criptomonedas del usuario se guardan en billeteras custodiales "
         "con seguros y auditorias. El usuario no necesita manejar claves "
         "privadas. Proveedor: Fireblocks o Circle Programmable Wallets."],
        ["Rampas de conversion", "Widgets integrados para que el usuario compre cripto con "
         "tarjeta o transferencia sin salir de la app. "
         "Proveedores: MoonPay o Transak."],
    ]
    pdf.table_header(["Componente", "Como Funciona"], w_fiat)
    for i, row in enumerate(crypto):
        pdf.table_row(row, w_fiat, fill=(i % 2 == 0))

    pdf.add_page()
    pdf.sub_title("Flujo Completo del Dinero")
    pdf.body("Como se mueve el dinero dentro del ecosistema LlanoPay:")
    pdf.ln(2)
    pdf.bullet("1. CARGA: El usuario deposita COP via PSE, tarjeta, Nequi o efectivo")
    pdf.bullet("2. BILLETERA: Los pesos se reflejan en su billetera digital (saldo COP)")
    pdf.bullet("3. TRANSFERENCIA: Puede enviar a otro usuario por celular (P2P)")
    pdf.bullet("4. PAGO: Puede pagar en comercios del marketplace con QR")
    pdf.bullet("5. CONVERSION: Puede convertir COP a cripto (BTC, ETH, USDT) o a Llanocoin (LLO)")
    pdf.bullet("6. CREDITO: Puede solicitar microcredito basado en su score de uso")
    pdf.bullet("7. RETIRO: Puede retirar a su cuenta bancaria, Nequi o Daviplata")
    pdf.bullet("8. REMESAS: Puede enviar/recibir remesas internacionales via USDC")

    pdf.ln(5)
    pdf.sub_title("Costos Operativos por Transaccion")
    costos = [
        ["Carga via PSE", "$3,400 COP fijo", "0.5% al usuario"],
        ["Carga via tarjeta", "2.5% al operador", "2.5% al usuario"],
        ["Carga en efectivo", "$2,000-3,000 COP", "Gratis o $1,000 al usuario"],
        ["Transferencia P2P", "~$200 COP interno", "0.5-1.5% al usuario"],
        ["Pago a comercio", "~$200 COP interno", "1.5-2.5% al comercio"],
        ["Compra de cripto", "0.1-0.6% del exchange", "1-2% al usuario"],
        ["Retiro a banco", "$2,000-4,000 COP", "0.5% al usuario"],
        ["SMS de verificacion", "$30 COP (~$0.0075 USD)", "Incluido"],
    ]
    w_cost = [50, 55, 75]
    pdf.table_header(["Operacion", "Costo Proveedor", "Costo al Usuario"], w_cost)
    for i, row in enumerate(costos):
        pdf.table_row(row, w_cost, fill=(i % 2 == 0))

    # ==================== REGULACION ====================
    pdf.add_page()
    pdf.section_title("Regulacion y Cumplimiento")

    pdf.body(
        "Para operar legalmente en Colombia con dinero real, LlanoPay debe cumplir "
        "con el marco regulatorio financiero colombiano:"
    )
    pdf.ln(3)

    reg = [
        ["Superintendencia Financiera (SFC)", "Registro como Sociedad Especializada en Depositos y Pagos "
         "Electronicos (SEDPE) o alianza con entidad vigilada. El sandbox regulatorio "
         "de la SFC permite operar temporalmente mientras se obtiene licencia completa."],
        ["SARLAFT", "Sistema de Administracion del Riesgo de Lavado de Activos y Financiacion "
         "del Terrorismo. Obligatorio para cualquier entidad que maneje dinero. Incluye "
         "KYC (Conoce a tu Cliente), monitoreo de transacciones sospechosas, y reportes."],
        ["UIAF", "Reportes periodicos a la Unidad de Informacion y Analisis Financiero. "
         "Reporte de Operaciones Sospechosas (ROS). "
         "Reporte de Transacciones en Efectivo superiores a $10,000,000 COP."],
        ["Ley 1581/2012 (Habeas Data)", "Proteccion de datos personales. Politica de privacidad, "
         "consentimiento explicito del usuario, derecho a consulta, correccion y "
         "supresion de datos. Registro de bases de datos ante la SIC."],
        ["Ley 1735/2014 (SEDPE)", "Marco legal para Sociedades Especializadas en Depositos y "
         "Pagos Electronicos. Define requisitos de capital, gobierno corporativo, "
         "gestion de riesgos y proteccion al consumidor."],
        ["Circular 029/2014 SFC", "Requerimientos tecnologicos: seguridad de la informacion, "
         "continuidad del negocio, gestion de riesgos operativos, "
         "canales electronicos seguros."],
    ]
    w_reg = [52, 128]
    pdf.table_header(["Regulacion", "Requisito"], w_reg)
    for i, row in enumerate(reg):
        pdf.table_row(row, w_reg, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("KYC (Conoce a tu Cliente) - Niveles")
    kyc = [
        ["Nivel 1 - Basico", "Solo celular + OTP", "Saldo max $3,000,000. Transacciones limitadas.", "2 min"],
        ["Nivel 2 - Verificado", "Cedula + selfie + datos personales", "Saldo max $15,000,000. Todas las funciones.", "24 hrs"],
        ["Nivel 3 - Premium", "Verificacion avanzada + soporte financiero", "Sin limites. Acceso a microcredito y cripto.", "48 hrs"],
    ]
    w_kyc = [32, 48, 70, 20]
    pdf.table_header(["Nivel", "Requisitos", "Beneficios", "Tiempo"], w_kyc)
    for i, row in enumerate(kyc):
        pdf.table_row(row, w_kyc, fill=(i % 2 == 0))

    # ==================== TRACCION ====================
    pdf.add_page()
    pdf.section_title("Plan de Traccion")

    pdf.sub_title("Fase 1: Lanzamiento (Meses 1-6)")
    pdf.bullet("Lanzamiento en Villavicencio (capital del Meta, 530,000 habitantes)")
    pdf.bullet("Alianza con 100 comercios locales para pagos QR")
    pdf.bullet("Campana en universidades: UNILLANOS, UNIMINUTO, Santo Tomas")
    pdf.bullet("Meta: 10,000 usuarios registrados, 3,000 activos mensuales")
    pdf.bullet("Alianza con cooperativas ganaderas del Meta")
    pdf.bullet("Programa de referidos: $5,000 COP por cada amigo que se registre")

    pdf.ln(3)
    pdf.sub_title("Fase 2: Expansion Regional (Meses 7-12)")
    pdf.bullet("Expansion a Yopal (Casanare) y Arauca")
    pdf.bullet("Alianza con empresas petroleras para pago de nomina digital")
    pdf.bullet("Lanzamiento del microcredito para pequenos productores")
    pdf.bullet("Meta: 30,000 usuarios registrados, 15,000 activos")
    pdf.bullet("Alianza con gremios: FEDEGAN, SAC, Camara de Comercio")

    pdf.ln(3)
    pdf.sub_title("Fase 3: Consolidacion (Meses 13-18)")
    pdf.bullet("Cobertura total de los 6 departamentos llaneros")
    pdf.bullet("Lanzamiento de Llanocoin (LLO) con programa de recompensas")
    pdf.bullet("Integracion de criptomonedas y remesas internacionales")
    pdf.bullet("Meta: 50,000 usuarios activos, $2,000 millones COP en transacciones/mes")
    pdf.bullet("Aplicacion al sandbox regulatorio de la SFC para licencia SEDPE")

    pdf.ln(3)
    pdf.sub_title("Fase 4: Escalamiento Nacional (Meses 19-24)")
    pdf.bullet("Expansion a otras regiones rurales de Colombia")
    pdf.bullet("Alianzas con bancos para interoperabilidad")
    pdf.bullet("Lanzamiento de tarjeta fisica prepagada LlanoPay")
    pdf.bullet("Meta: 150,000 usuarios activos, break-even operativo")

    # ==================== PROYECCIONES ====================
    pdf.add_page()
    pdf.section_title("Proyecciones Financieras")

    pdf.sub_title("Proyeccion a 3 Anos")
    proy = [
        ["Usuarios registrados", "10,000", "50,000", "200,000"],
        ["Usuarios activos mensuales", "3,000", "25,000", "100,000"],
        ["Transacciones/mes", "15,000", "200,000", "1,500,000"],
        ["Volumen transado/mes", "$300M COP", "$5,000M COP", "$50,000M COP"],
        ["Ingreso por comisiones/mes", "$3M COP", "$60M COP", "$600M COP"],
        ["Ingreso por microcredito/mes", "$0", "$15M COP", "$150M COP"],
        ["Ingreso por cripto/mes", "$0", "$5M COP", "$80M COP"],
        ["Ingreso total mensual", "$3M COP", "$80M COP", "$830M COP"],
        ["Ingreso total anual", "$36M COP", "$960M COP", "$9,960M COP"],
        ["Costos operativos/mes", "$25M COP", "$50M COP", "$350M COP"],
        ["Resultado neto/mes", "-$22M COP", "$30M COP", "$480M COP"],
        ["Comercios afiliados", "100", "500", "2,000"],
    ]
    w_proy = [55, 40, 45, 40]
    pdf.table_header(["Metrica", "Ano 1", "Ano 2", "Ano 3"], w_proy)
    for i, row in enumerate(proy):
        pdf.table_row(row, w_proy, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.highlight_box("  Break-even estimado: Mes 14-16 con 20,000 usuarios activos")

    # ==================== EQUIPO ====================
    pdf.add_page()
    pdf.section_title("Equipo Necesario")

    pdf.body(
        "Para llevar LlanoPay a produccion y escalar se necesita un equipo "
        "multidisciplinario con experiencia en fintech y la region:"
    )
    pdf.ln(3)

    equipo = [
        ["CEO / Fundador", "Liderazgo, vision, relaciones comerciales y regulatorias", "Conocimiento de los Llanos, redes en el sector financiero"],
        ["CTO", "Arquitectura, seguridad, infraestructura", "Experiencia en plataformas de pagos o fintech"],
        ["Desarrollador Backend", "API, integraciones con pasarelas, blockchain", "Experiencia en sistemas transaccionales"],
        ["Desarrollador Mobile", "Aplicacion movil, UX/UI", "Experiencia en apps de consumo masivo"],
        ["Oficial de Cumplimiento", "SARLAFT, KYC, reportes UIAF", "Certificacion en prevencion de lavado de activos"],
        ["Growth / Marketing", "Adquisicion de usuarios, alianzas comerciales", "Experiencia en productos de consumo en Colombia"],
        ["Soporte al Cliente", "Atencion 24/7, resolucion de problemas", "Conocimiento de la region y sus necesidades"],
    ]
    w_eq = [38, 65, 77]
    pdf.table_header(["Rol", "Responsabilidad", "Perfil Ideal"], w_eq)
    for i, row in enumerate(equipo):
        pdf.table_row(row, w_eq, fill=(i % 2 == 0))

    # ==================== INVERSION ====================
    pdf.ln(8)
    pdf.section_title("Inversion Requerida")

    inv = [
        ["Desarrollo de producto (6 meses)", "$80,000,000 COP", "Completar app, integraciones, seguridad"],
        ["Infraestructura y servidores (1 ano)", "$15,000,000 COP", "Cloud, dominios, certificados, SMS"],
        ["Licencias y regulacion", "$30,000,000 COP", "Asesoria legal, sandbox SFC, SARLAFT"],
        ["Marketing y adquisicion", "$40,000,000 COP", "Campanas, referidos, alianzas comerciales"],
        ["Equipo (6 meses nomina)", "$120,000,000 COP", "5-7 personas del equipo core"],
        ["Capital de trabajo", "$35,000,000 COP", "Operaciones, contingencias, fondo de reserva"],
        ["TOTAL", "$320,000,000 COP", "Aproximadamente $75,000 USD"],
    ]
    w_inv = [55, 40, 85]
    pdf.table_header(["Concepto", "Monto", "Detalle"], w_inv)
    for i, row in enumerate(inv):
        pdf.table_row(row, w_inv, fill=(i % 2 == 0))

    # ==================== HERRAMIENTAS ====================
    pdf.add_page()
    pdf.section_title("Herramientas y Proveedores Clave")

    pdf.body(
        "LlanoPay se construye sobre proveedores y herramientas especializadas "
        "que permiten operar de forma segura y escalable:"
    )
    pdf.ln(3)

    herr = [
        ["Pagos y pasarelas", "Wompi, PayU, ePayco", "Procesamiento de pagos PSE, tarjetas, Nequi"],
        ["Pagos en efectivo", "Efecty, Baloto, SuRed", "Recaudo en puntos fisicos a nivel nacional"],
        ["Exchange cripto", "Bitso, Binance", "Compra/venta de criptomonedas con COP"],
        ["Stablecoins", "Circle (USDC)", "Pagos internacionales y remesas en dolar digital"],
        ["Custodia cripto", "Fireblocks, Circle Wallets", "Almacenamiento seguro de criptomonedas"],
        ["On-ramp cripto", "MoonPay, Transak", "Compra de cripto con tarjeta/transferencia"],
        ["Verificacion de identidad", "Truora, Onfido", "Validacion automatica de cedula y selfie"],
        ["SMS y OTP", "Twilio, AWS SNS", "Envio de codigos de verificacion por SMS"],
        ["Notificaciones push", "Firebase Cloud Messaging", "Notificaciones en tiempo real al celular"],
        ["Cloud y servidores", "AWS, Google Cloud", "Infraestructura escalable y segura"],
        ["Monitoreo", "Sentry, DataDog", "Deteccion de errores y rendimiento"],
        ["Correo electronico", "SendGrid, AWS SES", "Comunicaciones transaccionales"],
    ]
    w_herr = [38, 47, 95]
    pdf.table_header(["Area", "Proveedor", "Uso"], w_herr)
    for i, row in enumerate(herr):
        pdf.table_row(row, w_herr, fill=(i % 2 == 0))

    # ==================== CONTACTO ====================
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(0, 120, 110)
    pdf.cell(0, 15, "LLANOPAY", align="C")
    pdf.ln(18)
    pdf.set_draw_color(0, 150, 136)
    pdf.set_line_width(1.5)
    pdf.line(55, pdf.get_y(), 155, pdf.get_y())
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "La billetera digital de los Llanos Orientales", align="C")
    pdf.ln(10)
    pdf.cell(0, 10, "Inclusion financiera para 2.5 millones de personas", align="C")
    pdf.ln(25)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Documento confidencial preparado para inversionistas", align="C")
    pdf.ln(10)
    pdf.cell(0, 8, "Abril 2026", align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 150, 136)
    pdf.cell(0, 8, "Contacto: [correo@llanopay.com]", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Web: [www.llanopay.com]", align="C")

    # Save
    output_path = r"C:\Users\HOME\PycharmProjects\llanopay\Portafolio_LlanoPay_Startup_2026.pdf"
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")


if __name__ == "__main__":
    generate()
