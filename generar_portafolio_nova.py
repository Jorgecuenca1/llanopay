from fpdf import FPDF


class PortfolioPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(75, 0, 130)
            self.cell(0, 8, "NovaPay | Global Digital Wallet", align="R")
            self.ln(4)
            self.set_draw_color(75, 0, 130)
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
        self.set_text_color(75, 0, 130)
        self.cell(0, 14, title)
        self.ln(10)
        self.set_draw_color(75, 0, 130)
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
        self.set_fill_color(245, 240, 255)
        self.set_draw_color(75, 0, 130)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(75, 0, 130)
        y = self.get_y()
        self.rect(10, y, 190, 14, style="DF")
        self.set_xy(15, y + 3)
        self.cell(0, 8, text)
        self.ln(18)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(75, 0, 130)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 8, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(50, 50, 50)
        if fill:
            self.set_fill_color(245, 240, 255)
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
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 20, "NOVAPAY", align="C")
    pdf.ln(22)
    pdf.set_draw_color(75, 0, 130)
    pdf.set_line_width(2)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(14)
    pdf.set_font("Helvetica", "", 17)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "The Global Digital Wallet", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Send money anywhere. Pay anything.", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Crypto, fiat, and beyond.", align="C")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Startup Portfolio", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "April 2026", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Confidential Document", align="C")

    # ==================== VISION ====================
    pdf.add_page()
    pdf.section_title("Vision")
    pdf.body(
        "NovaPay is a next-generation digital wallet built for a borderless world. "
        "We believe money should move as freely as information. No borders, no delays, "
        "no exclusion. Whether you are a freelancer in Lagos receiving payment from New York, "
        "a family in Manila sending remittances from Dubai, or a merchant in Bogota accepting "
        "crypto payments, NovaPay is your single financial hub."
    )
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 10, "Mission")
    pdf.ln(9)
    pdf.body(
        "To provide universal access to financial services for every person on the planet, "
        "regardless of location, income, or banking status. We combine the best of traditional "
        "finance with the power of blockchain to create a truly inclusive financial ecosystem."
    )

    pdf.ln(3)
    pdf.highlight_box("  One app. Every currency. Every country. Zero barriers.")

    # ==================== THE PROBLEM ====================
    pdf.add_page()
    pdf.section_title("The Problem")

    pdf.body(
        "The global financial system is fragmented, expensive, and excludes billions. "
        "Despite technological advances, basic financial services remain inaccessible "
        "for a massive portion of the world's population:"
    )
    pdf.ln(3)

    pdf.sub_title("Global Financial Exclusion")
    pdf.bullet("1.4 billion adults worldwide have no bank account (World Bank 2024)")
    pdf.bullet("Remittance fees average 6.2% globally - costing migrants $48 billion/year in fees")
    pdf.bullet("Cross-border transfers take 3-5 business days through traditional banking")
    pdf.bullet("Currency conversion fees range from 2-8% depending on corridor")
    pdf.bullet("76% of Sub-Saharan Africa and 65% of Southeast Asia are underbanked")
    pdf.bullet("Small merchants in emerging markets pay 3-5% for card processing")
    pdf.bullet("Freelancers in developing countries lose 5-10% on international payment platforms")

    pdf.ln(3)
    pdf.sub_title("Current Solutions Fall Short")
    pdf.bullet("Banks: Expensive, slow, require physical presence, exclude low-income users")
    pdf.bullet("PayPal/Wise: Limited in emerging markets, high fees for small amounts")
    pdf.bullet("Crypto wallets: Too complex for mainstream users, no fiat integration")
    pdf.bullet("Mobile money (M-Pesa): Regional, no cross-border, no crypto, no credit")
    pdf.bullet("Neobanks (Revolut, N26): Focused on developed markets, limited global reach")

    pdf.ln(3)
    pdf.highlight_box("  $150 trillion moves cross-border annually. We capture the underserved segment.")

    # ==================== THE SOLUTION ====================
    pdf.add_page()
    pdf.section_title("The Solution")

    pdf.body(
        "NovaPay is an all-in-one global digital wallet that unifies fiat currencies, "
        "cryptocurrencies, and financial services into a single, beautiful app. "
        "Available in 180+ countries from day one via smartphone."
    )
    pdf.ln(3)

    features = [
        ["Multi-Currency Wallet", "Hold and manage 50+ fiat currencies and 20+ cryptocurrencies "
         "in one wallet. Real-time conversion at interbank rates. No hidden fees. "
         "Supports USD, EUR, GBP, COP, MXN, NGN, PHP, INR, BRL, and more."],
        ["Instant Global Transfers", "Send money to anyone, anywhere, in seconds. P2P transfers "
         "by phone number, email, or username. Cross-border payments settle in under "
         "60 seconds via blockchain rails. Fees starting at 0.3%."],
        ["Crypto Trading & Custody", "Buy, sell, and hold Bitcoin, Ethereum, USDC, and 20+ tokens. "
         "Institutional-grade custody with insurance. Earn yield on stablecoins. "
         "Seamless fiat-to-crypto conversion."],
        ["NovaCoin (NOVA)", "Native utility token powering the ecosystem. Earn NOVA through "
         "transactions, referrals, and staking. Spend NOVA for fee discounts, "
         "premium features, and merchant rewards. Deflationary tokenomics."],
        ["Merchant Payments", "Accept payments from any NovaPay user worldwide via QR code, "
         "payment link, or API. Settle in local currency or crypto. "
         "Fees 60% lower than traditional card processing."],
        ["Micro-Lending", "AI-powered credit scoring based on transaction history and behavior. "
         "Microloans from $10 to $10,000 USD equivalent. Instant approval. "
         "Collateralized lending with crypto assets."],
        ["Virtual & Physical Cards", "Issue virtual Visa/Mastercard cards instantly. Spend your "
         "NovaPay balance anywhere cards are accepted. Physical card available "
         "in 50+ countries. Apple Pay and Google Pay compatible."],
        ["Bill Payments & Top-ups", "Pay bills, utilities, mobile top-ups in 100+ countries. "
         "Schedule recurring payments. Split bills with friends. "
         "Earn NOVA cashback on every payment."],
    ]
    w = [38, 142]
    pdf.table_header(["Feature", "Description"], w)
    for i, row in enumerate(features):
        pdf.table_row(row, w, fill=(i % 2 == 0))

    # ==================== VALUE PROPOSITION ====================
    pdf.add_page()
    pdf.section_title("Value Proposition")

    pdf.sub_title("For Users")
    pdf.bullet("Open an account in 90 seconds with just a phone number")
    pdf.bullet("Send $200 to another country for $0.60 (vs $12.40 industry average)")
    pdf.bullet("Hold multiple currencies and convert at real exchange rates")
    pdf.bullet("Access credit based on your financial behavior, not your zip code")
    pdf.bullet("Earn passive income on stablecoins (4-8% APY)")
    pdf.bullet("One app replaces: bank account + remittance service + crypto exchange + payment app")

    pdf.ln(4)
    pdf.sub_title("For Merchants")
    pdf.bullet("Accept payments from 180+ countries with zero hardware required")
    pdf.bullet("Fees from 0.8% (vs 2.9-3.5% for Stripe/PayPal)")
    pdf.bullet("Instant settlement in local currency, crypto, or stablecoins")
    pdf.bullet("Built-in loyalty program via NovaCoin rewards")
    pdf.bullet("API and plugins for e-commerce integration (Shopify, WooCommerce)")
    pdf.bullet("Analytics dashboard with real-time sales data")

    pdf.ln(4)
    pdf.sub_title("For Freelancers & Remote Workers")
    pdf.bullet("Receive payments from clients worldwide with zero conversion delays")
    pdf.bullet("Invoice in any currency, receive in any currency")
    pdf.bullet("Withdraw to local bank account, mobile money, or crypto wallet")
    pdf.bullet("Tax-ready transaction reports by country")

    pdf.ln(4)
    pdf.sub_title("For Enterprises")
    pdf.bullet("Payroll disbursement to 180+ countries in one click")
    pdf.bullet("Treasury management with multi-currency and stablecoin support")
    pdf.bullet("Compliance-ready KYC/AML integration")
    pdf.bullet("White-label wallet solution available")

    # ==================== BUSINESS MODEL ====================
    pdf.add_page()
    pdf.section_title("Business Model")

    pdf.body(
        "NovaPay generates revenue through diversified streams, ensuring resilience "
        "and compounding growth as the user base scales:"
    )
    pdf.ln(3)

    modelo = [
        ["Transaction Fees", "0.3% to 1.5% per transaction depending on type and volume. "
         "P2P transfers: 0.3-0.5%. Cross-border: 0.5-1.0%. "
         "Merchant payments: 0.8-1.5%. Volume-based pricing for enterprises."],
        ["FX Spread", "0.3-0.8% spread on currency conversions. Interbank rates + small markup. "
         "Competitive with Wise (0.4-1.5%) and far below banks (2-5%). "
         "High-frequency revenue stream."],
        ["Crypto Trading Fees", "0.1-0.5% per crypto trade. Lower than Coinbase (1.5%) and "
         "competitive with Binance (0.1%). Maker/taker fee model. "
         "Volume discounts for active traders."],
        ["Lending Interest", "8-24% APR on microloans (varies by market and risk). "
         "Crypto-collateralized loans at 5-12% APR. "
         "Net interest margin: 4-10% after cost of capital."],
        ["Staking & Yield", "Revenue share on stablecoin yield products. Users earn 4-8% APY, "
         "NovaPay earns 1-3% management fee. DeFi yield optimization."],
        ["NovaCoin Ecosystem", "1% fee on NOVA buy/sell. Token burn mechanism creates deflation. "
         "Enterprise partnerships for branded rewards programs."],
        ["Premium Subscriptions", "NovaPay Pro: $9.99/month - zero fees on transfers, higher limits, "
         "priority support, exclusive yield products. "
         "NovaPay Business: $29.99/month - advanced API, analytics, team accounts."],
        ["Card Revenue", "Interchange fees on card transactions (0.5-1.5%). "
         "Revenue share with Visa/Mastercard network. "
         "Card issuance fees in select markets."],
        ["B2B / White-Label", "Enterprise licensing for white-label wallet solutions. "
         "API access fees for payment processing. "
         "Custom integrations for banks and fintechs."],
    ]
    w_mod = [38, 142]
    pdf.table_header(["Revenue Stream", "Detail"], w_mod)
    for i, row in enumerate(modelo):
        pdf.table_row(row, w_mod, fill=(i % 2 == 0))

    # ==================== MARKET ====================
    pdf.add_page()
    pdf.section_title("Market Opportunity")

    pdf.sub_title("TAM (Total Addressable Market)")
    pdf.body(
        "Global digital payments market: $11.6 trillion (2025), projected $19.9 trillion by 2028. "
        "Global remittance market: $860 billion (2025). "
        "Global crypto market cap: $2.8 trillion. "
        "Combined TAM: $15+ trillion in annual transaction volume."
    )

    pdf.sub_title("SAM (Serviceable Available Market)")
    pdf.body(
        "Emerging markets digital payments: $3.2 trillion. "
        "Cross-border remittances to LATAM, Africa, Asia: $540 billion. "
        "Crypto retail trading in target markets: $180 billion. "
        "SAM: $3.9 trillion in addressable volume."
    )

    pdf.sub_title("SOM (Serviceable Obtainable Market)")
    pdf.body(
        "Initial target: LATAM (Colombia, Mexico, Brazil) + West Africa (Nigeria, Ghana) + "
        "Southeast Asia (Philippines, Indonesia). "
        "Year 3 target: $2.5 billion in annual transaction volume. "
        "At 0.8% average take rate = $20 million annual revenue."
    )

    pdf.ln(3)
    pdf.highlight_box("  $15 trillion TAM growing at 15% CAGR. We start where others don't reach.")

    pdf.ln(3)
    pdf.sub_title("Competitive Landscape")
    comp = [
        ["PayPal / Venmo", "Global", "Brand trust, merchant network", "High fees, limited in emerging markets, no crypto custody"],
        ["Wise (TransferWise)", "Global", "Low FX fees, transparency", "No crypto, no lending, no merchant payments, no rewards"],
        ["Revolut", "Europe+", "Multi-currency, crypto, cards", "Limited in Africa/LATAM/Asia, regulatory challenges"],
        ["Binance / Coinbase", "Global", "Crypto liquidity, brand", "No fiat wallet, complex UX, no remittances, no lending"],
        ["M-Pesa", "Africa", "Mobile money leader, offline", "Regional only, no crypto, no cross-border, no cards"],
        ["NovaPay", "Global", "All-in-one: fiat + crypto + lending + cards + rewards. "
         "Built for emerging markets first. 0.3% fees.", "New brand, requires initial traction"],
    ]
    w_comp = [28, 18, 62, 72]
    pdf.table_header(["Player", "Reach", "Strength", "Weakness"], w_comp)
    for i, row in enumerate(comp):
        pdf.table_row(row, w_comp, fill=(i % 2 == 0))

    # ==================== MONEY FLOW ====================
    pdf.add_page()
    pdf.section_title("How Money Moves in NovaPay")

    pdf.body(
        "NovaPay orchestrates money movement through regulated financial partners. "
        "We never hold customer funds directly - they are held in segregated accounts "
        "with licensed banking partners and insured custodians."
    )
    pdf.ln(3)

    pdf.sub_title("Fiat On/Off Ramps (By Region)")
    fiat = [
        ["Latin America", "PSE, SPEI, PIX, OXXO", "Bank transfers, mobile wallets, cash networks. "
         "Partners: Wompi, PayU, Mercado Pago, dLocal."],
        ["Africa", "Mobile Money, bank transfer", "M-Pesa, MTN MoMo, Airtel Money, Chipper Cash. "
         "Partners: Flutterwave, Paystack, dLocal."],
        ["Southeast Asia", "GCash, GrabPay, bank transfer", "Mobile wallets, bank direct debit, OTC. "
         "Partners: Xendit, PayMongo, dLocal."],
        ["Europe", "SEPA, Open Banking, cards", "Instant SEPA transfers, PSD2 open banking. "
         "Partners: Stripe, Adyen, TrueLayer."],
        ["North America", "ACH, Debit/Credit cards", "Bank transfers, Plaid-powered linking. "
         "Partners: Stripe, Plaid, Synapse."],
        ["Middle East", "Bank transfer, exchange houses", "Local bank integration, cash pickup. "
         "Partners: Checkout.com, Tabby, dLocal."],
        ["Global Cash", "Cash deposit networks", "200,000+ cash-in points worldwide. "
         "Partners: Efecty, OXXO, 7-Eleven, Paxful."],
    ]
    w_fiat = [30, 42, 108]
    pdf.table_header(["Region", "Methods", "Details"], w_fiat)
    for i, row in enumerate(fiat):
        pdf.table_row(row, w_fiat, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Crypto Infrastructure")
    crypto = [
        ["Liquidity & Trading", "Bitso, Binance, Kraken", "Multi-exchange aggregation for best prices. "
         "Deep liquidity pools. Supports 20+ tokens."],
        ["Stablecoins", "Circle (USDC), Tether (USDT)", "Dollar-pegged tokens for remittances and savings. "
         "On-chain settlement in seconds."],
        ["Custody", "Fireblocks, BitGo", "Institutional-grade MPC custody with $250M insurance. "
         "SOC 2 Type II certified. Cold + warm storage."],
        ["On-Ramp Widgets", "MoonPay, Transak, Ramp", "Embeddable buy/sell crypto with local payment methods. "
         "KYC-integrated. 180+ countries supported."],
        ["Blockchain Networks", "Polygon, Ethereum, Solana, Base", "Multi-chain support for low-fee transactions. "
         "NOVA token deployed on Polygon for gas efficiency."],
        ["DeFi Yield", "Aave, Compound, Yearn", "Automated yield strategies on stablecoins. "
         "Risk-scored products for users. Audited protocols only."],
    ]
    w_crypto = [32, 46, 102]
    pdf.table_header(["Layer", "Partners", "Details"], w_crypto)
    for i, row in enumerate(crypto):
        pdf.table_row(row, w_crypto, fill=(i % 2 == 0))

    # ==================== USER FLOW ====================
    pdf.add_page()
    pdf.sub_title("Complete User Journey")
    pdf.body("How a user interacts with NovaPay from signup to daily use:")
    pdf.ln(2)
    pdf.bullet("1. SIGNUP: Download app, enter phone number, verify via SMS OTP (90 seconds)")
    pdf.bullet("2. KYC: Scan ID + selfie for full verification (automated, 2-5 minutes)")
    pdf.bullet("3. FUND: Add money via bank transfer, card, mobile money, or cash deposit")
    pdf.bullet("4. HOLD: Balance visible in local currency + crypto. Multi-currency view.")
    pdf.bullet("5. SEND: Transfer to anyone by phone/email/username. Instant. From 0.3% fee.")
    pdf.bullet("6. PAY: Scan QR at merchants, pay online, or use virtual/physical card")
    pdf.bullet("7. CONVERT: Swap between fiat currencies at interbank rates (0.3% spread)")
    pdf.bullet("8. TRADE: Buy/sell crypto directly from the app. Instant execution.")
    pdf.bullet("9. EARN: Stake stablecoins for 4-8% APY. Earn NOVA on every transaction.")
    pdf.bullet("10. BORROW: Request microloan based on transaction history. Instant approval.")
    pdf.bullet("11. WITHDRAW: Cash out to bank account, mobile money, or crypto wallet")

    pdf.ln(5)
    pdf.sub_title("Transaction Costs to User")
    costos = [
        ["Domestic P2P transfer", "FREE (up to $500/month)", "0.3% after free tier"],
        ["Cross-border transfer", "0.5% (avg $1 on $200)", "vs $12.40 industry avg"],
        ["Currency conversion", "0.3% spread", "vs 2-5% at banks"],
        ["Crypto buy/sell", "0.5%", "vs 1.5% at Coinbase"],
        ["Merchant payment", "FREE for buyers", "0.8-1.5% to merchant"],
        ["Card payment", "FREE", "Interchange paid by merchant"],
        ["ATM withdrawal", "2 free/month", "$1.50 after free tier"],
        ["Bill payment", "FREE", "Varies by biller"],
        ["Stablecoin yield", "No fee to user", "NovaPay earns 1-3% mgmt fee"],
        ["Microloan", "8-24% APR", "Based on risk scoring"],
    ]
    w_cost = [50, 55, 75]
    pdf.table_header(["Operation", "Cost to User", "Notes"], w_cost)
    for i, row in enumerate(costos):
        pdf.table_row(row, w_cost, fill=(i % 2 == 0))

    # ==================== REGULATION ====================
    pdf.add_page()
    pdf.section_title("Regulatory Strategy")

    pdf.body(
        "NovaPay takes a compliance-first approach. We partner with licensed entities "
        "in each jurisdiction and pursue our own licenses as we scale. Our regulatory "
        "strategy is designed for rapid market entry while maintaining full compliance."
    )
    pdf.ln(3)

    reg = [
        ["United States", "MSB (FinCEN) + State MTLs", "Money Services Business registration. State-by-state "
         "Money Transmitter Licenses. Partnership with licensed banking partner initially."],
        ["European Union", "EMI License (EU-wide)", "Electronic Money Institution license under PSD2. "
         "Passportable across 27 EU countries. MiCA compliance for crypto."],
        ["United Kingdom", "FCA E-Money License", "Financial Conduct Authority registration. "
         "Crypto registration under FCA. Sandbox available."],
        ["Colombia", "SFC SEDPE License", "Superintendencia Financiera sandbox. SARLAFT compliance. "
         "UIAF reporting. Partnership with local bank."],
        ["Mexico", "CNBV IFPE License", "Fintech Law (Ley Fintech) compliance. CNBV registration "
         "for electronic payments. Crypto operations authorized."],
        ["Brazil", "BCB Payment Institution", "Banco Central do Brasil authorization. PIX integration. "
         "CVM registration for crypto operations."],
        ["Nigeria", "CBN PSB License", "Central Bank of Nigeria Payment Service Bank license. "
         "SEC registration for digital assets."],
        ["Philippines", "BSP EMI License", "Bangko Sentral ng Pilipinas registration. "
         "Virtual Currency Exchange license."],
        ["Global AML/KYC", "FATF Compliant", "Travel Rule compliance. Chainalysis integration for "
         "blockchain monitoring. Tier-based KYC (Basic/Verified/Premium)."],
    ]
    w_reg = [30, 40, 110]
    pdf.table_header(["Jurisdiction", "License", "Details"], w_reg)
    for i, row in enumerate(reg):
        pdf.table_row(row, w_reg, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("KYC Tiers (Global)")
    kyc = [
        ["Tier 0 - Basic", "Phone + email only", "$200/month limit. P2P only. No crypto.", "Instant"],
        ["Tier 1 - Verified", "Government ID + selfie", "$5,000/month. Full features. Crypto enabled.", "< 5 min"],
        ["Tier 2 - Enhanced", "Proof of address + source of funds", "$50,000/month. Higher limits. Lending access.", "< 24 hrs"],
        ["Tier 3 - Premium", "Full enhanced due diligence", "Unlimited. Enterprise features. Priority support.", "< 48 hrs"],
    ]
    w_kyc = [28, 43, 77, 22]
    pdf.table_header(["Tier", "Requirements", "Benefits", "Time"], w_kyc)
    for i, row in enumerate(kyc):
        pdf.table_row(row, w_kyc, fill=(i % 2 == 0))

    # ==================== TRACTION PLAN ====================
    pdf.add_page()
    pdf.section_title("Go-To-Market Strategy")

    pdf.sub_title("Phase 1: Foundation (Months 1-6)")
    pdf.bullet("Launch in Colombia and Mexico (LATAM beachhead)")
    pdf.bullet("Core features: wallet, P2P transfers, fiat on/off ramp, basic crypto")
    pdf.bullet("Partner with 500 merchants in Bogota, CDMX, Villavicencio")
    pdf.bullet("University ambassador program in 20 universities")
    pdf.bullet("Referral program: $5 USD in NOVA for each referred user")
    pdf.bullet("Target: 50,000 registered users, 15,000 MAU")

    pdf.ln(3)
    pdf.sub_title("Phase 2: LATAM Expansion (Months 7-12)")
    pdf.bullet("Expand to Brazil (PIX integration), Argentina, Peru, Chile")
    pdf.bullet("Launch NovaCoin (NOVA) token with staking rewards")
    pdf.bullet("Launch micro-lending in Colombia and Mexico")
    pdf.bullet("Virtual Visa card rollout across LATAM")
    pdf.bullet("Remittance corridors: US-Mexico, US-Colombia, Spain-LATAM")
    pdf.bullet("Target: 300,000 users, 100,000 MAU, $50M monthly volume")

    pdf.ln(3)
    pdf.sub_title("Phase 3: Africa & Asia (Months 13-18)")
    pdf.bullet("Launch in Nigeria, Ghana, Kenya (Africa) and Philippines, Indonesia (Asia)")
    pdf.bullet("Mobile money integration (M-Pesa, MTN MoMo, GCash)")
    pdf.bullet("Remittance corridors: UAE-Philippines, UK-Nigeria, US-India")
    pdf.bullet("Physical card rollout in top 10 markets")
    pdf.bullet("DeFi yield products for stablecoin holders")
    pdf.bullet("Target: 1M users, 400K MAU, $200M monthly volume")

    pdf.ln(3)
    pdf.sub_title("Phase 4: Global Scale (Months 19-24)")
    pdf.bullet("EU and UK launch with EMI/FCA licenses")
    pdf.bullet("B2B white-label solution for banks and fintechs")
    pdf.bullet("Enterprise payroll and treasury management")
    pdf.bullet("AI-powered fraud detection and credit scoring")
    pdf.bullet("Target: 3M users, 1.2M MAU, $1B monthly volume, profitability")

    # ==================== PROJECTIONS ====================
    pdf.add_page()
    pdf.section_title("Financial Projections")

    pdf.sub_title("3-Year Growth Forecast")
    proy = [
        ["Registered users", "50,000", "500,000", "3,000,000"],
        ["Monthly active users (MAU)", "15,000", "200,000", "1,200,000"],
        ["Monthly transactions", "75,000", "2,000,000", "15,000,000"],
        ["Monthly transaction volume", "$5M", "$200M", "$2.5B"],
        ["Avg transaction value", "$67", "$100", "$167"],
        ["Transaction fee revenue/mo", "$25K", "$1.2M", "$12.5M"],
        ["FX spread revenue/mo", "$5K", "$400K", "$5M"],
        ["Crypto trading revenue/mo", "$2K", "$200K", "$3M"],
        ["Lending interest revenue/mo", "$0", "$150K", "$2.5M"],
        ["Subscription revenue/mo", "$1K", "$100K", "$1.5M"],
        ["Card interchange revenue/mo", "$0", "$80K", "$1M"],
        ["Total monthly revenue", "$33K", "$2.1M", "$25.5M"],
        ["Total annual revenue", "$400K", "$25.2M", "$306M"],
        ["Monthly operating costs", "$150K", "$1.4M", "$15M"],
        ["Monthly net result", "-$117K", "$700K", "$10.5M"],
        ["Gross margin", "-", "67%", "59%"],
        ["Markets active", "2", "8", "25+"],
        ["Affiliated merchants", "500", "10,000", "100,000"],
    ]
    w_proy = [55, 35, 45, 45]
    pdf.table_header(["Metric", "Year 1", "Year 2", "Year 3"], w_proy)
    for i, row in enumerate(proy):
        pdf.table_row(row, w_proy, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.highlight_box("  Break-even: Month 16. Cash-flow positive by Month 20.")

    # ==================== NOVACOIN ====================
    pdf.add_page()
    pdf.section_title("NovaCoin (NOVA) - Token Economics")

    pdf.body(
        "NovaCoin (NOVA) is the native utility token of the NovaPay ecosystem. "
        "It aligns incentives between users, merchants, and the platform while "
        "creating a powerful network effect."
    )
    pdf.ln(3)

    pdf.sub_title("Token Utility")
    pdf.bullet("Fee discounts: Pay transaction fees with NOVA for 50% discount")
    pdf.bullet("Staking rewards: Stake NOVA to earn additional yield (8-15% APY)")
    pdf.bullet("Merchant rewards: Earn NOVA cashback on purchases (1-5%)")
    pdf.bullet("Governance: Vote on platform features and fee structures")
    pdf.bullet("Premium access: Stake NOVA to unlock premium features without subscription")
    pdf.bullet("Lending collateral: Use NOVA as collateral for microloans")

    pdf.ln(3)
    pdf.sub_title("Token Distribution")
    dist = [
        ["Community Rewards & Airdrops", "30%", "300,000,000", "Distributed over 5 years to users"],
        ["Team & Advisors", "20%", "200,000,000", "4-year vesting, 1-year cliff"],
        ["Treasury & Operations", "15%", "150,000,000", "Platform development and operations"],
        ["Investors (Seed + Series A)", "15%", "150,000,000", "2-year vesting, 6-month cliff"],
        ["Liquidity & Market Making", "10%", "100,000,000", "DEX and CEX liquidity pools"],
        ["Ecosystem Fund", "10%", "100,000,000", "Grants, partnerships, integrations"],
    ]
    w_dist = [50, 15, 35, 80]
    pdf.table_header(["Allocation", "%", "Tokens", "Notes"], w_dist)
    for i, row in enumerate(dist):
        pdf.table_row(row, w_dist, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.body(
        "Total supply: 1,000,000,000 NOVA (fixed). Deflationary mechanism: 20% of "
        "platform fees used to buy back and burn NOVA quarterly. Deployed on Polygon "
        "for low gas fees and fast transactions."
    )

    # ==================== TEAM ====================
    pdf.add_page()
    pdf.section_title("Team Requirements")

    pdf.body(
        "NovaPay requires a world-class team spanning fintech, blockchain, "
        "compliance, and growth. Key roles for the founding team:"
    )
    pdf.ln(3)

    equipo = [
        ["CEO / Co-Founder", "Vision, fundraising, partnerships, strategy", "Fintech or payments background. LATAM + global network."],
        ["CTO / Co-Founder", "Architecture, security, infrastructure, team building", "Scaled fintech platform. Blockchain expertise."],
        ["VP Engineering", "Backend, mobile, DevOps team leadership", "Built high-availability payment systems."],
        ["Head of Compliance", "Licensing, KYC/AML, regulatory relationships", "Multi-jurisdiction fintech compliance experience."],
        ["Head of Product", "UX/UI, user research, feature prioritization", "Consumer fintech products. Emerging market experience."],
        ["CMO (Chief Marketing Officer)", "Brand strategy, positioning, PR, content, paid media", "Built global fintech brand. Experience in emerging markets campaigns."],
        ["Head of Growth", "User acquisition, partnerships, viral loops", "Grew fintech/consumer app to 1M+ users."],
        ["Head of Crypto", "Token economics, DeFi, custody, blockchain ops", "Built or led crypto exchange or DeFi protocol."],
        ["Head of Risk", "Fraud prevention, credit scoring, risk modeling", "Financial risk management. ML/AI experience."],
        ["Country Managers", "Local operations, partnerships, compliance", "One per market. Deep local network."],
        ["Customer Support Lead", "24/7 multilingual support operations", "Scaled support for financial product."],
    ]
    w_eq = [35, 62, 83]
    pdf.table_header(["Role", "Responsibility", "Ideal Profile"], w_eq)
    for i, row in enumerate(equipo):
        pdf.table_row(row, w_eq, fill=(i % 2 == 0))

    # ==================== INVESTMENT ====================
    pdf.add_page()
    pdf.section_title("Investment")

    pdf.sub_title("Seed Round: $2.5M USD")
    pdf.body(
        "We are raising a $2.5M seed round to build the product, secure initial licenses, "
        "and launch in our first two markets (Colombia and Mexico)."
    )
    pdf.ln(3)

    inv = [
        ["Product Development (12 months)", "$800,000", "Engineering team, infrastructure, security audits"],
        ["Licensing & Legal", "$400,000", "MSB, SEDPE, IFPE applications. Legal counsel in 4 jurisdictions."],
        ["Team (12 months)", "$700,000", "Core team of 12-15 people across engineering, compliance, ops"],
        ["Marketing & User Acquisition", "$300,000", "Launch campaigns, referral program, ambassador network"],
        ["Infrastructure & Operations", "$150,000", "Cloud, SMS, custody, payment processor setup fees"],
        ["Working Capital & Reserve", "$150,000", "Operational buffer, contingencies, float management"],
        ["TOTAL SEED ROUND", "$2,500,000", "18-month runway to Series A milestones"],
    ]
    w_inv = [52, 25, 103]
    pdf.table_header(["Category", "Amount", "Detail"], w_inv)
    for i, row in enumerate(inv):
        pdf.table_row(row, w_inv, fill=(i % 2 == 0))

    pdf.ln(5)
    pdf.sub_title("Series A Milestones (Month 18)")
    pdf.bullet("300,000+ registered users across LATAM")
    pdf.bullet("$50M+ monthly transaction volume")
    pdf.bullet("$2M+ ARR (Annual Recurring Revenue)")
    pdf.bullet("Licenses secured in 3+ jurisdictions")
    pdf.bullet("NovaCoin launched and actively used by 50,000+ holders")
    pdf.bullet("Path to profitability demonstrated")

    pdf.ln(3)
    pdf.sub_title("Projected Series A: $15-25M USD")
    pdf.body(
        "Series A funds will accelerate expansion to Africa and Southeast Asia, "
        "launch the physical card program, build the lending book, and pursue "
        "EMI licensing in the EU/UK."
    )

    # ==================== TOOLS ====================
    pdf.add_page()
    pdf.section_title("Key Partners & Providers")

    pdf.body(
        "NovaPay leverages best-in-class providers to deliver a seamless "
        "global financial experience:"
    )
    pdf.ln(3)

    herr = [
        ["Payment Processing", "Stripe, Adyen, dLocal", "Global card and bank transfer processing"],
        ["LATAM Payments", "Wompi, PayU, Mercado Pago", "PSE, SPEI, PIX, local methods"],
        ["Africa Payments", "Flutterwave, Paystack", "Mobile money, bank transfers, cards"],
        ["Asia Payments", "Xendit, PayMongo", "GCash, GrabPay, local banks"],
        ["Crypto Exchange", "Bitso, Binance, Kraken", "Multi-exchange liquidity aggregation"],
        ["Stablecoins", "Circle (USDC)", "Dollar-pegged digital currency"],
        ["Crypto Custody", "Fireblocks, BitGo", "MPC custody with insurance"],
        ["Crypto On-Ramp", "MoonPay, Transak", "Buy crypto with local payment methods"],
        ["Card Issuance", "Marqeta, Visa DPS", "Virtual and physical card programs"],
        ["Identity Verification", "Onfido, Truora, Jumio", "Global KYC with document + biometric"],
        ["Blockchain Monitoring", "Chainalysis, Elliptic", "AML compliance for crypto transactions"],
        ["SMS & Communications", "Twilio, AWS SNS", "OTP, notifications, customer comms"],
        ["Push Notifications", "Firebase, OneSignal", "Real-time mobile notifications"],
        ["Cloud Infrastructure", "AWS, Google Cloud", "Multi-region, high-availability"],
        ["Monitoring & Security", "Sentry, DataDog, Cloudflare", "Error tracking, performance, DDoS protection"],
        ["Banking Partners", "Regional banks per market", "Segregated accounts, fiat custody"],
    ]
    w_herr = [35, 45, 100]
    pdf.table_header(["Category", "Provider", "Use Case"], w_herr)
    for i, row in enumerate(herr):
        pdf.table_row(row, w_herr, fill=(i % 2 == 0))

    # ==================== WHY NOW ====================
    pdf.add_page()
    pdf.section_title("Why Now?")

    pdf.bullet("Smartphone penetration in emerging markets surpassed 75% in 2025")
    pdf.bullet("Real-time payment infrastructure (PIX, UPI, SPEI) now available in key markets")
    pdf.bullet("MiCA regulation in EU provides clear crypto framework for the first time")
    pdf.bullet("Stablecoin market hit $180B, proving demand for digital dollars")
    pdf.bullet("Remote work created 200M+ cross-border freelancers needing payment solutions")
    pdf.bullet("Traditional banks are closing branches - 30% reduction since 2020")
    pdf.bullet("Gen Z and millennials (60% of emerging market population) are mobile-first")
    pdf.bullet("Open banking APIs now available in LATAM, Africa, and Asia")

    pdf.ln(5)
    pdf.sub_title("Why NovaPay Wins")
    pdf.bullet("EMERGING MARKETS FIRST: Built for the 1.4B unbanked, not as an afterthought")
    pdf.bullet("ALL-IN-ONE: Single app replaces 5+ financial products")
    pdf.bullet("CRYPTO-NATIVE: Blockchain rails for instant, cheap cross-border transfers")
    pdf.bullet("TOKEN ALIGNED: NovaCoin creates viral network effects and user retention")
    pdf.bullet("UNIT ECONOMICS: Positive at $100 average balance per user")
    pdf.bullet("REGULATORY READY: Compliance-first approach, not compliance-later")

    # ==================== CLOSING ====================
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 20, "NOVAPAY", align="C")
    pdf.ln(22)
    pdf.set_draw_color(75, 0, 130)
    pdf.set_line_width(2)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 15)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "The Global Digital Wallet", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "One app. Every currency. Every country.", align="C")
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(75, 0, 130)
    pdf.cell(0, 10, "Raising: $2.5M Seed Round", align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Contact: hello@novapay.io", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Web: www.novapay.io", align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Confidential - Prepared for investors - April 2026", align="C")

    # Save
    output_path = r"C:\Users\HOME\PycharmProjects\llanopay\Portafolio_NovaPay_Global_2026.pdf"
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")


if __name__ == "__main__":
    generate()
