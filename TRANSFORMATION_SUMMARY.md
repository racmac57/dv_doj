# DV Data Transformation Summary

## ✅ Completed Transformations

### 1. OffenseDate Column (Column M)
- **Original**: Column named `c` or `C`
- **Fixed**: Renamed to `OffenseDate`
- **Data Type**: Date-only (no time component)
- **Note**: In Excel/CSV exports, dates appear as datetime but represent date-only values

### 2. MunicipalityCode
- **Status**: All values are `"0 2 2 3"` (constant)
- **Action**: Column kept but noted as constant
- **Recommendation**: Could be removed or moved to metadata if desired

### 3. Time Column
- **Data Type**: `timedelta64` (duration)
- **Purpose**: Time-only data type for time values
- **Note**: In Excel, timedelta is converted to numeric, but CSV preserves structure better

### 4. TotalTime Column
- **Data Type**: `timedelta64` (duration)
- **Purpose**: Duration data type for time spans
- **Note**: Excel converts to numeric; consider formatting in Excel as time duration

### 5. VictimAge Column
- **Data Type**: `int64` (numeric)
- **Status**: Already numeric - kept as integer type
- **Recommendation**: Age should remain numeric for calculations

### 6. VictimRace Consolidation
**Before**: Multiple boolean columns
- `VictimRace_W`, `VictimRace_A`, `VictimRace_B`, `VictimRace_P`, `VictimRace_I`, `VictimRace_U`

**After**: Single column `VictimRace` with codes
- **W** - White
- **A** - Asian
- **B** - Black/African American
- **P** - Native Hawaiian/Other Pacific Islander
- **I** - American Indian/Alaska Native
- **U** - Unknown

**Result**: Reduced from 6 columns to 1 column
- Distribution: W=690, B=532, A=68, U=14, P=9, I=3

### 7. VictimEthnicity Consolidation
**Before**: Two boolean columns
- `VictimEthnic_H`, `VictimEthnic_NH`

**After**: Single column `VictimEthnicity` with codes
- **H** - Hispanic
- **NH** - Non-Hispanic

**Result**: Reduced from 2 columns to 1 column
- Distribution: NH=763, H=565

### 8. VictimSex Column Renaming
**Before**: 
- `VictimSexF`, `VictimSexM`

**After**:
- `FemaleVictim`, `MaleVictim`

**Status**: More descriptive column names

### 9. DayOfWeek Consolidation
**Before**: Seven boolean columns
- `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`

**After**: Single column `DayOfWeek` with abbreviated codes
- **Sun** - Sunday
- **Mon** - Monday
- **Tue** - Tuesday
- **Wed** - Wednesday
- **Thu** - Thursday
- **Fri** - Friday
- **Sat** - Saturday

**Result**: Reduced from 7 columns to 1 column
- Distribution: Sun=233, Sat=201, Wed=188, Mon=181, Fri=164, Tue=164, Thu=157

## 📊 Column Reduction Summary

- **Before**: 268 columns
- **After**: 256 columns
- **Reduction**: 12 columns removed (6 race + 2 ethnicity + 7 day of week - 1 new race - 1 new ethnicity - 1 new day of week = net -15 + 3 new = -12)

## 📁 Output Files

1. **`processed_data/_2023_2025_10_31_dv_fixed_transformed.xlsx`**
   - Excel format with all transformations

2. **`processed_data/_2023_2025_10_31_dv_fixed_transformed.csv`**
   - CSV format for easy import into other tools

## 🔧 Scripts

- **`transform_dv_data.py`**: Main transformation script
- **`verify_transformations.py`**: Verification script to check transformations

## 📝 Data Type Notes

### Excel Limitations
Excel doesn't natively support:
- Date-only (without time) - stored as datetime with 00:00:00 time
- Timedelta (duration) - converted to numeric (days as fraction)
- Pure time values - stored as datetime

### Recommendations for Excel Users
1. **OffenseDate**: Format column as "Date" only (no time display)
2. **Time/TotalTime**: Format as time duration or keep as days (numeric)
3. **VictimAge**: Format as number (no decimals)

### CSV/Parquet Format
For better data type preservation, consider using:
- **Parquet format**: Preserves all data types exactly
- **CSV with schema**: Can specify data types on import

## 🚀 Usage

### Re-run transformations:
```bash
python transform_dv_data.py
```

### Verify transformations:
```bash
python verify_transformations.py
```

## ✅ Transformation Checklist

- [x] OffenseDate column renamed and set to date-only
- [x] MunicipalityCode noted as constant
- [x] Time column converted to timedelta64
- [x] TotalTime column converted to timedelta64
- [x] VictimAge kept as numeric (int64)
- [x] VictimRace consolidated (6 → 1 column)
- [x] VictimEthnicity consolidated (2 → 1 column)
- [x] Sex columns renamed (FemaleVictim, MaleVictim)
- [x] DayOfWeek consolidated (7 → 1 column)
- [x] Data saved to Excel and CSV

## 🔄 Next Steps

1. Re-run the mapping script to use transformed file:
   ```bash
   python map_dv_to_rms_locations.py
   ```
   (Update to use transformed file)

2. Consider further consolidations:
   - OffenderRace (similar to VictimRace)
   - Other boolean flag columns
   - Relationship columns

3. For ArcGIS Pro:
   - Use the transformed file with consolidated columns
   - Easier to create categorical symbology with single columns

