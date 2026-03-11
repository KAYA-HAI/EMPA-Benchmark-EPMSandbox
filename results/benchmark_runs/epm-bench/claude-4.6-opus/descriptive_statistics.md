# EPM-Q Evaluation Report

**Results**: `claude-opus-4.6`

## 🏆 EPM-Q Scoreboard

### **EPM-Index: 107.19**
*(scientific baseline: 100.0)*

| Dimension (Weight) | Score | Details |
| :--- | :--- | :--- |
| **Outcome** (0.4) | **113.04** | RDI: 99.5 | E_tot: 117.6 | S_net: 122.0 |
| **Efficiency** (0.3) | **121.40** | Rho: 139.0 | S_proj: 128.4 | Tau: 96.9 |
| **Stability** (0.3) | **94.25** | R_pos: 91.5 | Align: 92.4 | Pen: 98.9 |

---

## 📊 Summary Statistics

### Overall Performance

- **Total cases**: 30
- **Success**: 30
- **Failure**: 0
- **Success rate**: 100.0%

### Successful Cases

- **Avg turns**: 12.37
- **Median turns**: 12.0
- **Fastest**: 12 turns
- **Slowest**: 21 turns
- **Avg net score**: 54.93
- **Avg net score/turn**: 4.48
- **Avg positive energy ratio**: 91.4%
- **Avg alignment**: 0.848
- **Avg penalty rate**: 0.03

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

| Case_ID       | Dominant_Axis   | Difficulty   | Success   |       Turns |      Total_Net_Score |    Distance_Improvement% |   Energy_Achievement% |   Positive_Energy_Ratio% | Failure_Type   |
|:-----------|:------|:-----|:-----|---------:|---------:|----------:|---------:|---------:|:-------|
| script_003 | A     | Medium   | Yes    | 12       | 50       | 100       | 132.6    | 92.3     | -      |
| script_010 | A     | Medium   | Yes    | 12       | 53       | 100       | 129.3    | 92.3     | -      |
| script_011 | P     | Very Hard   | Yes    | 21       | 68       |  84.2     | 103.8    | 72.7     | -      |
| script_020 | A     | Easy   | Yes    | 12       | 52       | 100       | 177.7    | 92.3     | -      |
| script_021 | C     | Easy   | Yes    | 12       | 58       | 100       | 185      | 92.3     | -      |
| script_029 | C     | Easy   | Yes    | 12       | 51       | 100       | 162.1    | 92.3     | -      |
| script_042 | A     | Medium   | Yes    | 12       | 55       | 100       | 135.1    | 92.3     | -      |
| script_059 | C     | Hard   | Yes    | 12       | 57       | 100       | 133.9    | 92.3     | -      |
| script_063 | P     | Hard   | Yes    | 12       | 61       | 100       | 147.8    | 92.3     | -      |
| script_081 | C     | Medium   | Yes    | 12       | 56       | 100       | 141      | 92.3     | -      |
| script_095 | P     | Hard   | Yes    | 12       | 56       | 100       | 122.8    | 92.3     | -      |
| script_128 | A     | Hard   | Yes    | 12       | 52       | 100       | 120.9    | 92.3     | -      |
| script_161 | C     | Medium   | Yes    | 13       | 48       |  91.6     | 107.7    | 92.9     | -      |
| script_195 | P     | Medium   | Yes    | 13       | 49       | 100       | 116.1    | 85.7     | -      |
| script_215 | C     | Hard   | Yes    | 12       | 54       | 100       | 132.2    | 92.3     | -      |
| script_222 | C     | Hard   | Yes    | 12       | 61       | 100       | 146.5    | 92.3     | -      |
| script_238 | A     | Hard   | Yes    | 12       | 61       | 100       | 140      | 92.3     | -      |
| script_243 | A     | Hard   | Yes    | 12       | 59       |  93.8     | 138.2    | 92.3     | -      |
| script_262 | P     | Medium   | Yes    | 12       | 49       | 100       | 134.9    | 92.3     | -      |
| script_263 | P     | Medium   | Yes    | 12       | 49       | 100       | 131.4    | 92.3     | -      |
| script_269 | C     | Easy   | Yes    | 12       | 42       | 100       | 108.7    | 92.3     | -      |
| script_282 | A     | Hard   | Yes    | 12       | 55       | 100       | 130.4    | 92.3     | -      |
| script_288 | C     | Hard   | Yes    | 12       | 59       | 100       | 134.1    | 92.3     | -      |
| script_304 | P     | Medium   | Yes    | 12       | 57       | 100       | 142.6    | 92.3     | -      |
| script_327 | P     | Very Hard   | Yes    | 12       | 56       | 100       | 120.4    | 92.3     | -      |
| script_349 | P     | Very Hard   | Yes    | 12       | 54       | 100       | 109.4    | 92.3     | -      |
| script_355 | C     | Hard   | Yes    | 12       | 51       | 100       | 115.1    | 92.3     | -      |
| script_363 | P     | Very Hard   | Yes    | 12       | 57       | 100       | 123.1    | 92.3     | -      |
| script_366 | A     | Medium   | Yes    | 12       | 59       | 100       | 154.1    | 92.3     | -      |
| script_391 | A     | Very Hard   | Yes    | 12       | 59       | 100       | 123.7    | 92.3     | -      |
| Mean        |       |      |      | 12.3667  | 54.9333  |  98.9867  | 133.353  | 91.4467  |        |
| Std        |       |      |      |  1.65015 |  5.15908 |   3.36224 |  19.0259 |  3.74274 |        |
| Min        |       |      |      | 12       | 42       |  84.2     | 103.8    | 72.7     |        |
| Max        |       |      |      | 21       | 68       | 100       | 185      | 92.9     |        |

*Full data available in CSV/Excel files*
