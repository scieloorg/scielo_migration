'''
Criar um script separado.

img
table

references
cada paragrafo é um item da lista

https://www.scielo.cl/scielo.php?script=sci_arttext&pid=S0716-97602015000100053

Procurar um mais antigo
    procurar ciencias-biologicas

Converter tudo
E gravar o resultado final num arquivo externo.


document.xml_body_and_back é a lista dos resultados
'''
from rich import print
from scielo_classic_website.spsxml.sps_xml_body_pipes import convert_html_to_xml
from lxml import etree


def get_tree(xml_str):
    return etree.fromstring(xml_str)


def tree_tostring_decode(_str):
    return etree.tostring(_str, encoding="utf-8").decode("utf-8")


def pretty_print(_str):
    return etree.tostring(get_tree(_str), encoding="utf-8", pretty_print=True).decode("utf-8")


class IncompleteDocument:

    def __init__(self):
        self.main_html_paragraphs = {
            "before references": [
                {
                    "text": '<!--version=html--> <p align="right"><font size="2" face="Verdana, Arial, Helvetica, sans-serif"><b>RESEARCH    ARTICLE</b></font></p>     ',
                    "index": "1",
                    "reference_index": "",
                    "part": "before references",
                },
                {
                    "text": '<p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="4"><b><a name="top"></a>Antioxidant    and anti hyperglycemic role of wine grape powder in rats fed with a high fructose    diet</b></font></p>     ',
                    "index": "2",
                    "reference_index": "",
                    "part": "before references",
                },
                {
                    "text": '<p>&nbsp;</p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Romina Hern&aacute;ndez-Salinas<sup>I</sup>;    Valerie Decap<sup>I</sup>; Alberto Leguina<sup>I</sup>; Patricio C&aacute;ceres<sup>I</sup>;    Druso Perez<sup>II</sup>; Ines Urquiaga<sup>II</sup>; Rodrigo Iturriaga<sup>I</sup><sup>,    </sup><sup>II</sup>; Victoria Velarde<sup>I, II, <a href="#back">*</a></sup></b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><sup>I</sup>Departamento    de Fisiolog&iacute;a, Facultad de Ciencias Biol&oacute;gicas, Pontif&iacute;cia    Universidad Cat&oacute;lica de Chile, Santiago, Chile    <br>   <sup>II</sup>Center for Molecular Nutrition and Chronic Diseases, Pontif&iacute;cia    Universidad Cat&oacute;lica de Chile, Santiago, Chile</font></p>     <p>&nbsp;</p>     <p>&nbsp;</p> <hr noshade size="1">     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>ABSTRACT</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>BACKGROUND</b>:    Metabolic syndrome is a growing worldwide health problem. We evaluated the effects    of wine grape powder (WGP), rich in antioxidants and fiber, in a rat model of    metabolic syndrome induced by a high fructose diet. We tested whether WGP supplementation    may prevent glucose intolerance and decrease oxidative stress in rats fed with    a high fructose diet.    <br>   <b>METHODS</b>: Male Sprague-Dawley rats weighing 180 g were divided into four    groups according to their feeding protocols. Rats were fed with control diet    (C), control plus 20 % WGP (C + WGP), 50 % high fructose (HF) or 50 % fructose    plus 20 % WGP (HF + WGP) for 16 weeks. Blood glucose, insulin and triglycerides,    weight, and arterial blood pressure were measured. Homeostasis model assessment    (HOMA) index was calculated using insulin and glucose values. A glucose tolerance    test was performed 2 days before the end of the experiment. As an index of oxidative    stress, thio-barbituric acid reactive substances (TBARS) level was measured    in plasma and kidney, and superoxide dismutase was measured in the kidney.    <br>   <b>RESULTS</b>: Thiobarbituric acid reactive substances in plasma and renal    tissue were significantly higher when compared to the control group. In addition,    the area under the curve of the glucose tolerance test was higher in HF fed    animals. Furthermore, fasting blood glucose, plasma insulin levels, and the    HOMA index, were also increased. WGP supplementation prevented these alterations    in rats fed with the HF diet. We did not find any significant difference in    body weight or systolic blood pressure in any of the groups.    <br>   <b>CONCLUSIONS</b>: Our results show that WGP supplementation prevented hyperglycemia,    insulin resistance and reduced oxidative stress in rats fed with HF diet. We    propose that WGP may be used as a supplement in human food as well.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Keywords</b>:    Insulin resistance, Oxidative stress, Metabolic syndrome, Wine grape powder</font></p> <hr noshade size="1">     <p>&nbsp;</p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>Background</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The development    of industrialized countries together with technological advances has produced    strong social changes that directly affect the human lifestyle. Changes in diet    and a sedentary lifestyle characterized by the lack of exercise in daily life    advance in parallel with a growing number of metabolic diseases, resulting in    high cardiovascular risk and increased morbidity and mortality rate. The association    of a collection of risk factors including hypertension, high triglycerides,    low HDL cholesterol, and high fasting glucose, which are linked to type 2 diabetes,    cardiovascular disease and stroke, created a condition called metabolic syndrome    (MS). The World Health Organization defines MS as a prothrombotic state, with    dyslipidemia, alteration in the metabolism of glucose, a sustained rise in blood    pressure, abdominal obesity and a systemic pro-inflammatory state [1]. The metabolic    syndrome has high prevalence, estimated between 20 and 30 % of adult worldwide    population [2, 3]. Abdominal obesity, one of the MS features, produces oxidative    stress. Accordingly, it has been found that an increased oxidative stress in    abdominal adipocytes may increase various pro-inflammatory cytokines and fatty    acids, which exacerbate other MS factors such as insulin resistance, hypertriglyceridemia,    and hypertension [4]. In addition, it has been demonstrated that the activity    of several antioxidant enzymes decreases in humans with MS [5]. One of the transcription    factors responsible for the initiation of the antioxidant response is the nuclear    factor E2-related factor-2 (Nrf2), which controls the expression of cellular    phase-2 detoxifying and anti-oxidant enzymes [6, 7]. Nrf2 induces the expression    of several antioxidant enzymes [8-11] such as superoxide dismutase (SOD) to    restore the imbalance of oxidative stress [12, 13].</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Because MS involves    several different factors, no unique pharmaceutical treatment exists to prevent    or treat it. The best solution seems to be to adjust lifestyle factors like    diet and exercise. It is known that grape anti-oxidants play a role in the reduction    of the metabolic syndrome risk factors. Grapes contain numerous antioxidants    such as polyphenols, anthocyanins, flavonols and resveratrol. A simple way to    make grape polyphenols part of the diet is to consume grape products. Wine grape    pomace is an underused residue of the wine making process. This grape by-product    contains pressed skins, seeds and stems and accounts for about 20 % of the weight    of the grapes used to make wine. In addition, grape pomace is a rich source    of polyphenols including monomeric and oligomeric proanthocyanidins and a diversity    of anthocyanin glycosides [14]. Due to the abundance of antioxidants found in    this by-product, grape pomace is increasingly being used to obtain functional    food ingredients and as a dietary supplement [15]. Flavonoids that are present    in grape pomace are a large group of polyphenolic antioxidants present in a    variety of foods. Most naturally occurring flavonoids can induce chelation of    transition metals, the scavenging of free radicals, and inhibition of radical    producing enzymes [16]. In addition, it has been postulated that a flavonoid-rich    diet can prevent several degenerative age-related diseases [17] and several    kinds of cancer [18]. It can also reduce the incidence of coronary heart disease    [15], and chronic renal disease [19]. As mentioned before, it is well accepted    that diets rich in polyphenols have health benefits, but the mechanisms of action    of these molecules in the human body are not fully understood [20-22]. Wine    grape powder (WGP) made from dried wine grape pomace, is rich in fiber and polyphenols.    However, little is known about the potential effects of WGP in the oxidative    state or metabolic markers of MS. Therefore, the present study was conducted    to investigate the antioxidant and anti-insulin-resistance effect of WGP in    an established rat model of MS induced by high fructose diet [23-26].</font></p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>Methods</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Wine grape powder</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Wine grape pomace,    a waste product from wine production was obtained from a single production lot    of red grapes (Cabernet Sauvignon, vintage 2011, Maipo Valley, Chile) from Concha    y Toro Winery, and stored at -20 &deg;C until used, for approximately 3 months.    The frozen wine grape pomace was thawed at room temperature and dried in a forced    air dryer at 60 &deg;C until moisture reached less than 12 %. The dried pomace    was grinded with a hammer mill to obtain a wine grape pomace powder (WGP), which    was packaged in double plastic bags of 20 kg. WGP has a high content of dietary    fiber (48 %) determined by AOAC 991.43. The content of polyphenolic compounds    was 41.11 &plusmn; 3.01 mg galic acid equivalent/g, determined by the Folin-Ciocalteu    procedure [27]. WGP with a high antioxidant capacity of 362.9 &plusmn; 24.4    </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">mol    TE/g, measured by the oxygen radical absorbance capacity assay [28].</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Rats, diets,    and treatment with WGP</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The experimental    protocols were approved by the Bio-ethical Committee of the Faculty of Biological    Sciences of the Pontificia Universidad Cat&oacute;lica de Chile and were in    accordance with the Guide for the Care and Use of Laboratory Animals published    by the US National Institutes of Health (NIH Publication No. 85-23, revised    1996). Male Sprague-Dawley rats (6 week old, 180 g) were obtained from the Faculty    of Biological Sciences Animal Care Facility. Rats were randomly divided into    4 groups according to their feeding treatments: control diet-fed rats (C; n    = 8), control diet-fed rats supplemented with WGP (C + WGP; 20 % of WGP; n =    8); high-fructose diet-fed rats (HF; 50 % fructose, n = 7) and high-fructose    diet-fed rats supplemented with WGP (HF + WGP, n = 6).</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Mixtures for each    of the diets were prepared on an industrial mixer at the Molino La Estampa,    Chile, using the proportions for each of the ingredients shown in <a href="#t1">Table    1</a>. Food pellets for each of the animal diets were prepared daily by adding    the same amount of water to a fraction of each of the powder mixtures.</font></p>     <p align="center"><a name="t1"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Table    1 Composition and energy provide by the experimental diets</b></font></p>     <p align="center"><img src="/fbpe/img/bres/v48/53t01.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><i>C</i>    control diet, <i>C</i> + <i>WGP</i> control diet plus 20 % wine grape powder,    <i>HF</i> high fructose diet, <i>HF</i> + <i>WGP</i> high fructose diet plus    20 % wine grape powder</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The proximate analysis    of the WGP is shown in <a href="#t2">Table 2</a>, and the composition and energy    provided by proteins, carbohydrates and fat in experimental diets is shown in    <a href="#t1">Table 1</a>. Animals were fed with 36 g (dry mixture) of their    respective diets daily for 16 weeks. Rats were individually housed under controlled    temperature, 12-h-light/dark cycles, consumed water ad libitum, <i>and were    </i>under veterinarian supervision.</font></p>     <p align="center"><a name="t2"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Table    2 Proximate analysis of wine grape flour</b></font></p>     <p align="center"><img src="/fbpe/img/bres/v48/53t02.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Total    dietary fiber corresponds to the sum of soluble and insoluble fractions    <br>   </font><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><sup>a</sup>    Nitrogen free extract minus dietary fiber</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>P</b><b>hysiological    and metabolic variables</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">All rats were continuously    monitored for body weight, food and water intake. Blood glucose and triglycerides    were measured using a commercial enzymatic kit and strips (Code Free, SD Biosensor    Inc, Korea). Oral glucose tolerance test (GTT) was performed 2 days before the    end of the experiment, on rats that have been food-deprived for 12 h. Each animal    received 2 g/kg of glucose diluted in 2 mL of water by gavage. Rats were anesthetized    with isofluorane 2 % in O<sub>2</sub>, and blood samples were obtained from    the tail vein at 0 min (before glucose administration) 30, 60 and 120 min. A    glucose tolerance curve was obtained and the trapezoidal rule was used to determine    the area under the curve (AUC).</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Arterial blood    pressure measurements</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Measurements of    systolic arterial blood pressure was performed with a non-invasive method in    conscious rats, in a room at 25 &deg;C, with noise and light control. These    measurements were done using a Power Lab coupled to a NIBP system with pulse    transducer/cuff for rat by tail cuff (ADInstruments, Australia). Rats were trained    at least for 1 month before the experimental measurements. In separate experimental    series, three rats were anesthetized with isofluorane 2 % in O<sub>2</sub> and    were implanted with radio-telemetric transmitters (TA11PA, DSI, USA) in one    femoral artery. After surgery, rats received Ketoprofen 0.2 mg/ kg (Rhodia Merieux)    and Enrofloxacin 20 mg/kg (Bayer) i.m. Rats were allowed to recover for 7 days    prior to the surgery and then were fed with control, high fructose and high    fructose + WGP diets for 120 days. Arterial blood pressure was averaged from    30 min recordings, performed between 9 and 10 AM every 3 days in the initial    90 days, and then every 10 days during the last 30 days.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Blood and tissue    samples</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">At the end of the    experiment, blood samples were taken, and then animals were sacrificed under    anesthesia (Xyla-sine/Ketamine, 10 mg/90 mg per kg). Kidneys were immediately    removed, frozen in liquid nitrogen and stored at -80 &deg;C for later determinations.    Plasma insulin level was determined using a rat insulin ELISA kit (EMD Millipore    Corporation, USA), calculating the homeosta-sis model assessment of insulin    resistance (HOMA-IR), based on the following formula:</font></p>     <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2">HOMA    - IR = serum glucose (mg/dL) x plasma insulin (</font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">U/ml)/405.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Oxidative stress    measurement</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Levels of thiobarbituric    acid reactive substances (TBARS) in the plasma and kidneys were estimated using    a previously described method [29] with slight modifications. 100 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">L    of plasma or supernatant from tissue homoge-nate were mixed with 50 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">L    sodium dodecyl sulphate (8 %w/v), 375 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">L    thiobarbituric acid (0.8 % w/v), and 375 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">L    acetic acid (20 %v/v); and then heated for 60 min at 90 &deg;C. The precipitated    material was removed by cen-trifugation, and the absorbance of the supernatant    was determined at 532 nm. Levels of TBARS were expressed as malondialdehyde    (MDA).</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Electrophoresis    and Western blot analysis</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">To determine relative    levels of Nrf-2 (1:500; Santa Cruz Biotechnology) and mSOD (1:2000, Millipore),    kidney homogenates were lysed in RIPA with protease inhibitors (1 mg/mL aminocaproic    acid, 1 mg/mL benzamidine, 0.2 mg/mL SBTI and 3 mmol/L PMSF) and phosphatase    inhibitors (12 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">g/mL    sodium orthovanadate, 4.46 mg/mL sodium pyrophosphate, and 4.2 mg/mL sodium    fluoride). Lysates were centrifuged and supernatants were collected for Western    blot analysis. Protein concentrations were determined by the method of Lowry    [30]. Protein samples (100 </font><font size="2">&#956;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">g)    from homogenates under different treatments were separated by electrophoresis    in 10 % SDS-poly-acrylamide gel (SDS-PAGE). Proteins were transferred to a 0.45    </font><font size="2">&#956;&#951;&#953;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">    PVDF membrane, which was blocked at room temperature with Tris pH 7.6/5 % skim    milk (w/v)/BSA 1 % (w/v). Then, the PVDF membrane was incubated overnight at    4 &deg;C with primary antibody, followed by incubation with rabbit secondary    antibody conjugated to peroxidase (1:2000) for 2 h. Immunoreactive bands were    visualized using a chemiluminescent reagent (Western Lightning, Perkin Elmer)    according to the procedure described by the supplier and Kodak films X-LS. The    bands detected were digitized and subjected to densitometric analysis using    the program Image J (NIH, Washington DC, USA).</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Statistical    analysis</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Data obtained from    different groups of rats were compared with each other by one-way analysis of    variance (ANOVA) followed by a Bonferroni\'s post hoc test. The analyses were    performed with GraphPad Prism 5 software for Windows (GraphPad Software). Results    are expressed as mean &plusmn; standard error of the mean (SEM). Differences    were considered significant if p <u>&lt;</u> 0.05.</font></p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>Results</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Effects of the    high fructose diet on the physiological parameters measured in rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">High fructose diet    increased glucose, triglycerides and insulin levels in plasma measured after    12 h of food deprivation, but did not induce changes in systolic arterial pressure,    body or heart weight (<a href="#t3">Table 3</a>). Supplementation with WGP to    the HF diet reduced the increase in glucose, triglycerides and insulin levels    in plasma. In a separate experimental series, we recorded systolic and diastolic    arterial pressure with radiotelemetry in three rats fed with control, high fructose    and high fructose plus WGP. Arterial blood pressure slightly increased during    the experiment in all groups. However a similar trend in the increase of arterial    blood pressure was observed in all three rats (<a href="#f1">Fig. 1</a>).</font></p>     <p align="center"><a name="t3"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Table    3 Physiological parameters of rats fed experimental diets</b></font></p>     <p align="center"><a href="/fbpe/img/bres/v48/53t03.jpg"><img src="/fbpe/img/bres/v48/53t03thumb.jpg" border="0"></a></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2">n    = 6-8 in each group    <br>   </font><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><i>C</i>    control diet, <i>C</i> + <i>WGP</i> control diet plus wine grape powder, <i>HF</i>    high fructose diet, <i>HF</i> + <i>WGP</i> high fructose diet plus wine grape    powder    <br>   </font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">* P &lt;    0.05 Bonferroni after one way ANOVA</font></p>     <p align="center">&nbsp;</p>     <p align="center"><a name="f1"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f01.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    1</b> Arterial blood pressure measured by radiotelemetry in three conscious    rats fed with control (C <i>filled circle</i>), high fructose (HF <i>filled    square</i>) and high fructose + WGP (HF + WGP <i>unfilled square</i>) diets.    Systolic and diastolic arterial blood pressure of the rats was displayed in    the <i>upper</i> and <i>lower</i> part of the figure, respectively. Telemeters    were implanted into the femoral artery and the recordings started 7 days after    the surgery. <i>Arrow</i> indicate the beginning of the diet treatments</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>WGP prevented    the rise of glucose and the area under the curve on the glucose tolerance test    in fructose-fed rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Rats treated with    a high fructose diet had the highest fasting level of blood glucose, before    beginning the GTT (<a href="#f2">Fig. 2a</a>). The GTT showed that the largest    increase in blood glucose measured at 30 min and 2 h following glucose administration    was observed in the HF group. In addition, it is worth to note that glucose    levels in the HF + WGP group were slightly lower than the one on the control    group, while the lowest curve was from the C + WGP group. To quantify these    differences, we measured the area under curve (AUC) of the glucose tolerance    test (<a href="#f2">Fig. 2b</a>). We found a significant increase in the area    under the curve in the HF fed group, whereas WGP prevented the increased AUC    in the WGP + HF treated rats.</font></p>     <p align="center"><a name="f2"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f02.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    2</b> WGP prevents the increase in the area under the curve for the glucose    tolerance test. <b>a</b> Glucose tolerance test curves are shown for control    (C <i>filled circle</i>), control + WGP (C + WGP <i>unfilled circle</i>) high    fructose (HF <i>filled square</i>) and high fructose + WGP (HF + WGP <i>unfilled    square</i>) fed animals. Each <i>curve</i> represents mean &plusmn; SEM for    at least six animals. <b>b</b> Area under the curve was calculated for the curve    of each animal. <i>Bars</i> represent mean &plusmn; SEM for n = 6-8 rats in    each group. *P &lt; 0.05 HF vs. other groups. Bonferroni after one way ANOVA</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>WGP prevented    the induction of insulin resistance in fructose-fed rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">To evaluate whether    the increase in the AUC correlates with the insulin concentration, we measured    insulin in the blood obtained after 12 h of starvation. Under these conditions,    we found that rats from the HF fed group presented the highest levels of insulin,    and its increase was prevented by the supplementation with WGP in the diet,    as observed from the HF + WGP fed group (<a href="#f3">Fig. 3a</a>). In addition,    glucose levels were measured in these same blood samples and the homeostasis    model assessment-estimated IR (HOMA-IR) index was evaluated for each group.    HF fed rats presented a significantly higher HOMA-IR index compared to control    rats. In addition, this increase was prevented in HF + WGP fed rats (<a href="#f3">Fig.    3b</a>).</font></p>     <p align="center"><a name="f3"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f03.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    3</b> WGP prevents insulin resistance in HF fed rats. a Insulin was measured    using a radioimmunoassay in control (C), control + WGP (C + WGP) high fructose    (HF) and high fructose + WGP (HF + WGP) fed animals. b HOMA was calculated from    insulin values shown in this figure and glucose values obtained at the same    time points. <i>Bars</i> represent mean &plusmn; SEM for n = 6-8 rats in each    group. *P &lt; 0.05 HF vs. other groups. Bonferroni after one way ANOVA</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>WGP prevented    the rise of TBARS in plasma from fructose-fed rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">High fructose diet    produced a significant threefold increase in plasma TBARS levels measured at    the end of 16 weeks of treatment (<a href="#f4">Fig. 4</a>). WGP effectively    prevented this increase in TBARS levels in high fructose-fed rats. When compared    to control, TBARS levels in HF + WGP were not significantly different from those    of control rats.</font></p>     <p align="center"><a name="f4"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f04.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    4</b> WGP reduces oxidative stress in HF fed rats. TBARS were measured in plasma    from control (C), control + WGP (C + WGP) high fructose (HF) and high fructose    + WGP (HF + WGP) diets. <i>Bars</i> represent mean &plusmn; SEM for n = 6-8    rats in each group. *P &lt; 0.05 HF vs. other groups. Bonferroni after one way    ANOVA</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>WGP prevented    the reduction of SOD protein levels in kidneys from fructose-fed rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Nrf-2 is considered    a key transcription factor in the cellular response to oxidative stress [31].    This transcription factor regulates the expression of several antioxidant enzymes    that participate in the defense against reactive oxygen species such as superoxide    dismutase (SOD). Therefore, we evaluated the effect of HF treatment on Nrf-2    levels in renal tissue and found no significant changes after 16 weeks of treatment    in this transcription factor. Although Nrf-2 protein levels were not significantly    modified by the diet, we speculated that its activity could be modified. For    this reason, we measured mSOD protein concentration, one of the proteins regulated    by Nrf-2. We found a significant reduction in renal mSOD levels. Consistent    with the previous observations, this decrease was not observed in HF rats fed    with WGP (<a href="#f5">Fig. 5</a>).</font></p>     <p align="center"><a name="f5"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f05.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    5</b> WGP prevents the reduction in renal mSOD protein levels. Protein extracts    from kidneys from control (C), control + WGP (C + WGP) high fructose (HF) and    high fructose + WGP (HF + WGP) fed animals were used to evaluate mSOD protein    levels. <i>Bars</i> represent mean &plusmn; SEM for n = 4 animals in each group.    Bars represent mean &plusmn; SEM for n = 4, *p &lt; 0.05 HF vs. other groups.    Bonferroni after one way ANOVA. Representative blots for mSOD and </font><font size="2">&#946;</font><font face="Verdana, Arial, Helvetica, sans-serif" size="2">-actin    used as loading control are shown under the graph</font></p>     <p align="center">&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>WGP prevents    the rise of TBARS in kidneys from fructose-fed rats</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">To determine whether    the changes in mSOD proteins levels correlated with the oxidative state found    in the kidney, we measured TBARS in renal tissue. We found a significant increase    in TBARS in the HF group, whereas this increase was prevented in the HF + WGP    fed group (<a href="#f6">Fig. 6</a>).</font></p>     <p align="center"><a name="f6"></a></p>     <p align="center">&nbsp;</p>     <p align="center"><img src="/fbpe/img/bres/v48/53f06.jpg"></p> <p align="center"><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Fig.    6</b> WGP prevented oxidative stress in renal tissue. Extracts from kidneys    from control (C), control + WGP (C + WGP) high fructose (HF) and high fructose    + WGP (HF + WGP) fed animals were used to determine TBARS. <i>Bars</i> represent    mean &plusmn; SEM for n = 6-8 rats in each group, *P &lt; 0.05 HF vs. other    groups. Bonferroni after one way ANOVA</font></p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>Discussion</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The main finding    of the current study is that 16 weeks of supplementation with WGP protects against    fructose-induced oxidative stress and glucose intolerance in a rat model of    metabolic syndrome. The metabolic syndrome is a growing health problem and it    is important to find a treatment to prevent its development. However, it is    difficult to find a single treatment, because of the multiple factors that participate    in this syndrome. The use of food supplements is one of the possible approaches    to prevent the progression of this syndrome. The presented results show that    WGP supplement prevents the evolution of the metabolic syndrome in rats.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Despite that arterial    blood pressure did not change, we found that the high-fructose diet produced    metabolic alterations similar to those found by others [23-26, 32]. Some studies    have reported an increase in body weight [23] and arterial blood pressure [24]    in rats treated with a high fructose diet, but other studies failed to find    changes in these variables in Sprague-Dawley rats [25, 26]. The difference with    other studies may reflect a differential response to stress of different strain    rats, or the methods to measure arterial blood pressure. However, we measured    arterial blood pressure in conscious rats using both radiotelemetry and the    tail cuff methods. Several studies have demonstrated the ability of a high fructose    diet to induce insulin resistance, reproducing the features of the metabolic    syndrome in laboratory rats [23-26, 32]. Similarly to other studies, we found    an increase of the area under curve of the glucose tolerance test, fasting blood    glucose, plasma insulin, the HOMA index, and TBARS in plasma and renal tissue    of HF-fed rats [23-26, 32].</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">It has been observed    that high fructose fed rats develop metabolic syndrome without requiring an    increased energy intake, because fructose is metabolized different than glucose    ultimately producing uric acid. Uric acid is an antioxidant in the extracellular    environment, but when enters the cells it induces an oxidative burst, mediated    by the NADPH oxidase. This burst can induce increases in arterial blood pressure    when affecting endothelial cells and in body weight. One explanation to the    absence of effect on body weight and arterial pressure in our model is that    in rats, uricase is expressed in high amounts so there is an efficient degradation    of uric acid. Nevertheless, it has been reported that fructose induces insulin    resistance even with high levels of uricase [33], and although we did not measure    uricase, we did observe insulin resistance in our experimental group.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Oxidative stress    is a feature of several metabolic disorders. Kunde et al. [34] evaluated the    oxidative stress in the liver of mice exposed to 30 % fructose diet, and found    an increase in TBARS, which did not reach significance. Similarly, Yin et al.    [35] found that TBARS increased in the hippocampus and cerebral cortex in Wistar    rats treated with 10 % fructose from 16 weeks. Moreover, they demonstrated that    these changes were prevented by the administration of Pioglitazone, an antihyperglycemic    drug. We found an increase in renal TBARS that correlates with the decrease    in the levels of mSOD. The ability of WGP to prevent the increases in TBARS    and the decreases in mSOD levels, suggests that WGP may be as effective as some    pharmacological drugs in preventing the alterations induced by fructose.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The effects of    WGP on oxidative stress and glucose intolerance found in this study could be    attributed to its high content in polyphenols. These compounds are found in    all plant species. They are important in plants for reproduction, growth, pigmentation    and protection against pathogens [36]. Polyphenols are abundant in the mediterranean    diet that is rich in fruits and wine. Grapes contain a great variety of polyphenols,    including resveratrol, flavonoids, flavonols, flavones and anthocya-nines. Polyphenols    can exert several effects. It has been postulated that polyphenols from green    tea, may reduce cholesterol and fatty acid absorption [37]. In addition, it    was shown that a lyophilized grape powder reduced the overall metabolism of    lipoproteins [38]. Patel et al. [39] showed that dietary polyphenols may attenuate    the inflammation through modulation of the activities of NF-kB and Nrf-2.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">When evaluating    one particular polyphenol, it has been reported that resveratrol, extracted    from grape skins, increases the activity of SIRT1 [40] and AMPK [41], and inhibits    the mitochondrial ATP synthase [42]. On the other hand, EGCG has been used to    inhibit several receptor tyrosine kinase activities such as the ones from vascular    endothelial growth factor receptor [43] and insulin like growth factor receptor    [44]. All together these results suggest that one or the combination of the    different polyphenols found in WGP may produce the beneficial effects observed    in the rats treated with HF and WGP on this study.</font></p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>Conclusions</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">In summary, the    present results show that WGP supplementation prevents glucose intolerance and    reduces oxidative stress in rats fed with high fructose diet. Accordingly, WGP    could be used as a food supplement for the prevention of the metabolic syndrome    in human. Nevertheless, further studies are needed to validate the use of this    flour in humans.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Abbreviations</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">WGP: wine grape    powder; HF: high fructose; HOMA: homeostasis model assessment; TBARS: thiobarbituric    acid reactive substances; HDL: high density lipoproteins; MS: metabolic syndrome;    Nrf2: nuclear factor E2-related factor-2; mSOD: mitochondrial superoxide dismutase;    GTT: oral glucose tolerance tests; AUC: area under the curve; MDA: malondialdehyde;    SBTI: soy bean trypsin inhibitor; PMSF: phenylmethylsulfonyl fluoride; BSA:    bovine serum albumin; PVDF: polyvinylidene difluoride.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Authors\' contributions</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">VV, RI, and IU    designed research. RH, VD, DP, and PC conducted research. VV, RI, and RH analyzed    data. VV, RI, RH, and AL wrote paper. VV had primary responsibility for final    content. All authors read and approved the final manuscript.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Financial support</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">This work was supported    by project Fondef AF 10i1014 from CONICYT, Chile and project Puente #20/2013,    PUC.</font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Compliance with    ethical guidelines</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><b>Competing interests</b></font></p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">The authors declare    that they have no competing interests.</font></p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="3"><b>References</b></font></p>     ',
                    "index": "3",
                    "reference_index": "",
                    "part": "before references",
                },
            ],
            "references": [
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">1. Haffner SM.    The metabolic syndrome: inflammation, diabetes mellitus, and cardiovascular    disease. Am J Cardiol. 2006;97:3A-11A.    </font></p>     ',
                    "index": "1",
                    "reference_index": "1",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">2. Grundy SM. Metabolic    syndrome pandemic. Arterioscler Thromb Vasc Biol. 2008;28:629-36.    </font></p>     ',
                    "index": "2",
                    "reference_index": "2",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">3. M&aacute;rquez-Sandoval    F, Macedo-Ojeda G, Viramontes-H&otilde;rner D, Fernandez Ballart JD, Salas Salvado    J, Vizmanos B. The prevalence of metabolic syndrome in Latin America: a systematic    review. Public Health Nutr. 2011;14:1702-13.    </font></p>     ',
                    "index": "3",
                    "reference_index": "3",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">4. Chung SW, Kang    SG, Rho JS, Kim HN, Song IS, Lee YA, et al. The association between oxidative    stress and metabolic syndrome in adults. Korean J Fam Med. 2013;34:420-8.    </font></p>     ',
                    "index": "4",
                    "reference_index": "4",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">5. Yubero-Serrano    EM, Delgado-Lista J, Pena-Orihuela P, Perez-Martinez P, Fuentes F, Marin C,    et al. Oxidative stress is associated with the number of components of metabolic    syndrome: LIPGENE study. Exp Mol Med. 2013;45:e28.    </font></p>     ',
                    "index": "5",
                    "reference_index": "5",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">6. Lee JM, Johnson    JA. An important role of Nrf2-ARE pathway in the cellular defense mechanism.    J Biochem Mol Biol. 2004;37:139-43.    </font></p>     ',
                    "index": "6",
                    "reference_index": "6",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">7. Lee JS, Surh    YJ. Nrf2 as a novel molecular target for chemoprevention. Cancer Lett. 2005;224:171-84.    </font></p>     ',
                    "index": "7",
                    "reference_index": "7",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">8. Asghar M, George    L, Lokhandwala MF. Exercise decreases oxidative stress and inflammation and    restores renal dopamine D1 receptor function in old rats. Am J Physiol Renal    Physiol. 2007;293:F914-9.    </font></p>     ',
                    "index": "8",
                    "reference_index": "8",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">9. Ishii T, Itoh    K, Takahashi S, Sato H, Yanagawa T, Katoh Y, et al. Transcription factor Nrf2    coordinately regulates a group of oxidative stress-inducible genes in macrophages.    J Biol Chem. 2000;275:16023-9.    </font></p>     ',
                    "index": "9",
                    "reference_index": "9",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">10. Kathirvel P,    Chen K, Morgan K, French SW, Morgan TR. Oxidative stress and regulation of anti-oxidant    enzymes in cytochrome P4502E1 transgenic mouse model of non-alcoholic fatty    liver. J Gastroenterol Hepatol. 2010;25:1136-43.    </font></p>     ',
                    "index": "10",
                    "reference_index": "10",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">12. Zhang HF, Shi    LJ, Song GY, Cai ZG, Wang C, An RJ. Protective effects of matrine against progression    of high-fructose diet-induced steatohepatitis by enhancing antioxidant and anti-inflammatory    defences involving Nrf2 translocation. Food Chem Toxicol. 2013;55:70-7.    </font></p>     ',
                    "index": "12",
                    "reference_index": "12",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">13. Wakabayashi    N, Dinkova-Kostova AT, Holtzclaw WD, Kang MI, Kobayashi A, Yamamoto M, et al.    Protection against electrophile and oxidant stress by induction of the phase    2 response: fate of cysteines of the Keap1 sensor modified by inducers. Proc    Natl Acad Sci USA. 2004;101:2040-5.    </font></p>     ',
                    "index": "13",
                    "reference_index": "13",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">14. Ky I, Lorrain    B, Kolbas N, Crozier A, Teissedre PL. Wine by-products: phenolic characterization    and antioxidant activity evaluation of grapes and grape pomaces from six different    French grape varieties. Molecules. 2014;19:482-506.    </font></p>     ',
                    "index": "14",
                    "reference_index": "14",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">15. Choi CS, Chung    HK, Choi MK, Kang MH. Effects of grape pomace on the antioxidant defense system    in diet-induced hypercholesterolemic rabbits. Nutr Res Pract. 2010;4:114-20.    </font></p>     ',
                    "index": "15",
                    "reference_index": "15",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">16. Lanningham-Foster    L, Chen C, Chance DS, Loo G. Grape extract inhibits lipid peroxidation of human    low density lipoprotein. Biol Pharm Bull. 1995;18:1347-51.    </font></p>     ',
                    "index": "16",
                    "reference_index": "16",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">17. Stevenson DE,    Hurst RD. Polyphenolic phytochemicals-just antioxidants or much more? Cell Mol    Life Sci. 2007;64:2900-16.    </font></p>     ',
                    "index": "17",
                    "reference_index": "17",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">18. Roginsky AB,    Ujiki MB, Ding XZ, Adrian TE. On the potential use of flavonoids in the treatment    and prevention of pancreatic cancer. In Vivo. 2005;19:61-7.    </font></p>     ',
                    "index": "18",
                    "reference_index": "18",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">19. Pech&aacute;nov&aacute;    O, Rezzani R, Bab&aacute;l P, Bern&aacute;tov&aacute; I, Andriantsitohaina R.    Beneficial effects of provinols: cardiovascular system and kidney. Physiol Res.    2006;55:S17-30.    </font></p>     ',
                    "index": "19",
                    "reference_index": "19",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">20. Manach C, Williamson    G, Morand C, Scalbert A, Remesy C. Bioavailability and bioefficacy of polyphenols    in humans. I. Review of 97 bioavailability studies. Am J Clin Nutr. 2005;81:230S-42S.    </font></p>     ',
                    "index": "20",
                    "reference_index": "20",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">21. Tang SY, Halliwell    B. Medicinal plants and antioxidants: what do we learn from ell culture and    <i>Caenorhabditis elegans </i>studies? Biochem Biophys Res Commun. 2010;394:1-5.    </font></p>     ',
                    "index": "21",
                    "reference_index": "21",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">22. Singleton VL,    Orthofer R, Lamuela-Raventos RM. Analysis of total phenols and other oxidation    substrates and antioxidants by means of Folin-Ciocalteu Reagent. Methods Enzymol.    1999;299:152-78.    </font></p>     ',
                    "index": "22",
                    "reference_index": "22",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">23. Choi HN, Park    YH, Kim JH, Kang MJ, Jeong SM, Kim HH, et al. Renoprotective and antioxidant    effects of <i>Saururus chinensis </i>Baill in rats fed a high- fructose diet.    Nutr Res Pract. 2011;5:365-9.    </font></p>     ',
                    "index": "23",
                    "reference_index": "23",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">24. Dhar I, Dhar    A, Wu L, Desai KM. Increased methylglyoxal formation with upregulation of renin    angiotensin system in fructose fed Sprague Dawley rats. PLoS One. 2013;8:e74212.    </font></p>     ',
                    "index": "24",
                    "reference_index": "24",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">25. D\'Angelo G,    Elmarakby AA, Pollock DM, David W, Stepp DW. Fructose feeding increases insulin    resistance but not blood pressure in Sprague-Dawley rats. Hypertension. 2005;46:806-11.    </font></p>     ',
                    "index": "25",
                    "reference_index": "25",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">26. Bezerra RMN,    Ueno M, Silva MS, Tavares DQ, Carvalho CRO, Saad MJA, Gontijo JAR. A high fructose    diet induces insulin resistance but not blood pressure changes in normotensive    rats. Braz J Medl Biol Res. 2001;34:1155-60.    </font></p>     ',
                    "index": "26",
                    "reference_index": "26",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">27. Gutteridge    JM, Halliwell B. Antioxidants: molecules, medicines, and myths. Biochem Biophys    Res Commun. 2010;393:561-4.    </font></p>     ',
                    "index": "27",
                    "reference_index": "27",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">28. Ou B, Hampsch-Woodill    M, Prior RL. Development and validation of an improved oxygen radical absorbance    capacity assay using fluorescein as the fluorescent probe. J Agric Food Chem.    2001;49:4619-26.    </font></p>     ',
                    "index": "28",
                    "reference_index": "28",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">29. Bors W, Saran    M. Radical scavenging by flavonoid antioxidants. Free Radic Res Commun. 1987;2:289-94.    </font></p>     ',
                    "index": "29",
                    "reference_index": "29",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">30. Lowry OH, Rosebrough    NJ, Farr AL, Randall RJ. Protein measurement with the folin phenol reagent.    J Biol Chem. 1951;193:265-75.    </font></p>     ',
                    "index": "30",
                    "reference_index": "30",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">31. Ray PD, Huang    BW, Tsuji Y. Reactive oxygen species (ROS) homeostasis and redox regulation    in cellular signaling. Cell Signal. 2012;24:981-90.    </font></p>     ',
                    "index": "31",
                    "reference_index": "31",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">32. Johnson RJ,    Nakagawa T, Sanchez-Lozada LG, Shafiu M, Sundaram S, Le M, et al. Sugar, uric    acid, and the etiology of diabetes and obesity. Diabetes. 2013;62:3307-15.    </font></p>     ',
                    "index": "32",
                    "reference_index": "32",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">33. Tapia E, Cristobal    M, Garc&iacute;a-Arroyo FE, Soto V, Monroy-S&aacute;nchez F, Pacheco U, et al.    Synergistic effect of uricase blockade plus physiological amounts of fructose-glucose    on glomerular hypertension and oxidative stress in rats. Am J Physiol Renal    Physiol. 2013;304:F727-36.    </font></p>     ',
                    "index": "33",
                    "reference_index": "33",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">34. Kunde SS, Roede    JR, Vos MB, Orr ML, Go Y-M, Park Y, et al. Hepatic oxidative stress in fructose-induced    fatty liver is not caused by sulfur amino acid insufficiency. Nutrients. 2011;3:987-1002.    </font></p>     ',
                    "index": "34",
                    "reference_index": "34",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">35. Yin Q-Q, Pei    J-J, Xu S, Luo D-Z, Dong S-Q, Sun M-H, et al. Pioglitazone improves cognitive    function via increasing insulin sensitivity and strengthening antioxidant defense    system in fructose-drinking insulin resistance rats. PLoS One. 2013;8:e59313.    </font></p>     ',
                    "index": "35",
                    "reference_index": "35",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">36. Zern TL, Fernandez    ML. Cardioprotective effects of dietary polyphenols. J Nutr. 2005;135:2291-4.    </font></p>     ',
                    "index": "36",
                    "reference_index": "36",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">37. L&ouml;est    HB, Noh SK, Koo SI. Green tea extract inhibits the lymphatic absorption of cholesterol    and alpha-tocopherol in ovariectomized rats. J Nutr. 2002;132:1282-8.    </font></p>     ',
                    "index": "37",
                    "reference_index": "37",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">38. Zern TL, West    KL, Fernandez ML. Grape polyphenols decrease plasma triglycerides and cholesterol    accumulation in the aorta of ovariectomized guinea pigs. J Nutr. 2003;133:2268-72.    </font></p>     ',
                    "index": "38",
                    "reference_index": "38",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">39. Patel R, Maru    G. Polymeric black tea polyphenols induce phase II enzymes via Nrf2 in mouse    liver and lungs. Free Radic Biol Med. 2008;44:1897-911.    </font></p>     ',
                    "index": "39",
                    "reference_index": "39",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">40. Howitz KT,    Bitterman KJ, Cohen HY, Lamming DW, Lavu S, Wood JG, et al. Small molecule activators    of sirtuins extend <i>Saccharomyces cerevisiae </i>lifespan. Nature. 2003;425:191-6.    </font></p>     ',
                    "index": "40",
                    "reference_index": "40",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">41. Zhang F, Sun    C, Wu J, He C, Ge X, Huang W, et al. Combretastatin a-4 activates AMP-activated    protein kinase and improves glucose metabolism in db/db mice. Pharmacol Res.    2008;57:318-23.    </font></p>     ',
                    "index": "41",
                    "reference_index": "41",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">42. Gledhill JR,    Montgomery MG, Leslie AG, Walker JE. Mechanism of inhibition of bovine F1 -ATPase    by resveratrol and related polyphenols. Proc Natl Acad Sci USA. 2007;104:13632-7.    </font></p>     ',
                    "index": "42",
                    "reference_index": "42",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">43. Kondo T, Ohta    T, Igura K, He C, Ge X, Huang W, et al. Tea catechins inhibit angiogenesis in    vitro, measured by human endothelial cell growth, migration and tube formation,    through inhibition of VEGF receptor binding. Cancer Lett. 2002;180:139-44.    </font></p>     ',
                    "index": "43",
                    "reference_index": "43",
                    "part": "references",
                },
                {
                    "text": '<!-- ref --><p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">44. Shimizu M,    Deguchi A, Hara Y, Moriwaki H, Weinstein IB. EGCG inhibits activation of the    insulin-like growth factor-1 receptor in human colon cancer cells. Biochem Biophys    Res Commun. 2005;334:947-53.    </font></p>',
                    "index": "44",
                    "reference_index": "44",
                    "part": "references",
                },
            ],
            "after references": [
                {
                    "text": '<p><font face="Verdana, Arial, Helvetica, sans-serif" size="2">Received: 13 June    2015    <br>   Accepted: 22 September 2015    <br>   Published online: 30 September 2015</font></p>     <p>&nbsp;</p>     <p>&nbsp;</p>     <p><font face="Verdana, Arial, Helvetica, sans-serif" size="2"><a name="back"></a><a href="#top">*</a>    Correspondence: <a href="mailto:vvelarde@bio.puc.cl">vvelarde@bio.puc.cl</a></font></p>      </div></div>',
                    "index": "",
                    "reference_index": "",
                    "part": "after references",
                }
            ],
        }

        self.translated_html_by_lang = {
            "pt": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>Depois das referencias 1</p>",
            },
            "en": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>After Reference</p>",
            },
        }


def save_file(filename, result):
    # tree = etree.ElementTree(result)
    with open(filename, 'w') as f:
        f.write(pretty_print(result))


def main():
    document = IncompleteDocument()

    convert_html_to_xml(document)

    result = document.xml_body_and_back

    for i, item in enumerate(result):
        print(pretty_print(item))
        save_file(f'/tmp/output_{i}.xml', item)


if __name__ == '__main__':
    main()