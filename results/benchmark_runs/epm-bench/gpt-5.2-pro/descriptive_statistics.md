# EPM-Q Evaluation Report

**Results**: `gpt-5.2-pro_20251225_162308`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 97.62**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **102.21** | RDI: 97.7 | E_tot: 95.5 | S_net: 113.4 |
| **Efficiency** (0.3) | **97.32** | Rho: 102.5 | S_proj: 95.3 | Tau: 94.2 |
| **Stability** (0.3) | **93.19** | R_pos: 89.9 | Align: 91.7 | Pen: 97.9 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 30
- **Failure**: 0
- **Success rate**: 100.0%

### Successful Cases

- **Avg turns**: 14.43
- **Median turns**: 13.0
- **Fastest**: 12 turns
- **Slowest**: 44 turns
- **Avg net score**: 51.67
- **Avg net score/turn**: 3.7
- **Avg positive energy ratio**: 89.9%
- **Avg alignment**: 0.835
- **Avg penalty rate**: 0.06

### By Dominant Axis

| Dominant Axis | Cases | Success Rate |
|-------|-------|-------|
| C | 10 | 100.0% |
| A | 10 | 100.0% |
| P | 10 | 100.0% |

### By Difficulty

| Difficulty | Cases | Success Rate |
|-----|-------|-------|
| Easy | 4 | 100.0% |
| Medium | 10 | 100.0% |
| Hard | 11 | 100.0% |
| Very Hard | 5 | 100.0% |

---

## 📋 Detailed Data Table

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |      Total_Net_Score |    Distance_Improvement% |    Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|---------:|----------:|----------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 12       |  48      | 100       | 121.7     |  92.3    | -      |
| script_010 | A     | Medium   | Yes    | 14       |  52      | 100       | 115       |  93.3    | -      |
| script_011 | P     | Very Hard   | Yes    | 44       | 108      |  65.7     | 103.5     |  64.4    | -      |
| script_020 | A     | Easy   | Yes    | 12       |  43      | 100       | 133.2     |  84.6    | -      |
| script_021 | C     | Easy   | Yes    | 12       |  41      |  95.7     | 106.5     |  92.3    | -      |
| script_029 | C     | Easy   | Yes    | 13       |  39      |  95.5     | 101.3     |  85.7    | -      |
| script_042 | A     | Medium   | Yes    | 13       |  48      | 100       | 103.7     |  92.9    | -      |
| script_059 | C     | Hard   | Yes    | 12       |  49      | 100       | 106.6     |  92.3    | -      |
| script_063 | P     | Hard   | Yes    | 12       |  52      | 100       | 114.8     |  92.3    | -      |
| script_081 | C     | Medium   | Yes    | 13       |  47      | 100       | 103.2     |  92.9    | -      |
| script_095 | P     | Hard   | Yes    | 12       |  51      |  94.2     | 105.9     |  92.3    | -      |
| script_128 | A     | Hard   | Yes    | 15       |  55      | 100       | 111.8     |  87.5    | -      |
| script_161 | C     | Medium   | Yes    | 18       |  52      |  96.3     | 104       |  89.5    | -      |
| script_195 | P     | Medium   | Yes    | 16       |  53      | 100       | 105.3     |  88.2    | -      |
| script_215 | C     | Hard   | Yes    | 12       |  51      | 100       | 117.8     |  92.3    | -      |
| script_222 | C     | Hard   | Yes    | 12       |  55      | 100       | 125       |  92.3    | -      |
| script_238 | A     | Hard   | Yes    | 15       |  54      |  93.5     | 103.3     |  93.8    | -      |
| script_243 | A     | Hard   | Yes    | 15       |  52      |  93.8     | 103.3     |  93.8    | -      |
| script_262 | P     | Medium   | Yes    | 14       |  46      |  92.3     | 104.7     |  93.3    | -      |
| script_263 | P     | Medium   | Yes    | 13       |  46      |  84.7     | 107.8     |  92.9    | -      |
| script_269 | C     | Easy   | Yes    | 12       |  42      | 100       | 104.3     |  84.6    | -      |
| script_282 | A     | Hard   | Yes    | 12       |  51      | 100       | 117.3     |  92.3    | -      |
| script_288 | C     | Hard   | Yes    | 12       |  51      | 100       | 108.1     |  92.3    | -      |
| script_304 | P     | Medium   | Yes    | 12       |  46      |  90       | 101.2     |  92.3    | -      |
| script_327 | P     | Very Hard   | Yes    | 13       |  52      |  88.6     | 101.2     |  92.9    | -      |
| script_349 | P     | Very Hard   | Yes    | 14       |  56      |  83.7     | 103.9     |  93.3    | -      |
| script_355 | C     | Hard   | Yes    | 17       |  50      |  90.9     | 101.2     |  72.2    | -      |
| script_363 | P     | Very Hard   | Yes    | 18       |  61      |  96       | 107.5     |  94.7    | -      |
| script_366 | A     | Medium   | Yes    | 12       |  47      | 100       | 105.4     |  92.3    | -      |
| script_391 | A     | Very Hard   | Yes    | 12       |  52      | 100       | 103.3     |  92.3    | -      |
| Mean        |       |      |      | 14.4333  |  51.6667 |  95.3633  | 108.393   |  89.9367 |        |
| Std        |       |      |      |  5.88208 |  11.6422 |   7.39555 |   7.85936 |   6.5374 |        |
| Min        |       |      |      | 12       |  39      |  65.7     | 101.2     |  64.4    |        |
| Max        |       |      |      | 44       | 108      | 100       | 133.2     |  94.7    |        |

*Full data available in CSV/Excel files*
