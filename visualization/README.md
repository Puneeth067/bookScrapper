
# 📊 Power BI Dashboard: Book Data Analysis

## 🗂️ Overview

This Power BI report provides an interactive and insightful analysis of book data scraped from an online bookstore. It includes data cleaning, transformation, DAX calculations, rich visuals, and drill-through capabilities to help users explore pricing, stock availability, and rating patterns effectively.

---

## 🛅 Data Import

### Steps:

1. Open **Power BI Desktop**
2. Go to **Home** > **Get Data** > **Text/CSV**
3. Load the dataset from: `scrapping/raw_data/books_data.csv`
4. Click **Transform Data** to clean and prepare the dataset

---

## 🧹 Data Cleaning (Power Query Editor)

Steps performed:

* Removed duplicates
* Trimmed whitespaces
* Standardized the `Availability` column to "In Stock" / "Out of Stock"
* Converted `Price` from text (`£33.34`) to numeric
* Converted prices from GBP to USD (`£1 = $1.32`)

### Sample M Code Snippet:

```m
let
    Source = Csv.Document(File.Contents("path/to/books_data.csv")),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    RemovedDuplicates = Table.Distinct(PromotedHeaders),
    CleanedPrice = Table.TransformColumns(RemovedDuplicates, {
        {"Price", each Number.FromText(Text.Replace(Text.Trim(_), "£", "")), type number}
    }),
    TrimmedText = Table.TransformColumns(CleanedPrice, {
        {"Title", Text.Trim}, {"Availability", Text.Trim}
    }),
    StandardizedAvailability = Table.TransformColumns(TrimmedText, {
        {"Availability", each if Text.Contains(Text.Lower(_), "in stock") then "In stock" else "Out of stock"}
    })
in
    StandardizedAvailability
```

---

## 🧾 DAX Calculations

### 🔁 Calculated Columns:

```dax
Price_USD = [Price] * 1.32

Price_Category =
IF([Price_USD] < 26.40, "Budget",
   IF([Price_USD] < 66, "Standard", "Premium"))
```

### 🕥 Measures:

```dax
Total Books = COUNTROWS(books_data)

Average Price = AVERAGE(books_data[Price_USD])

In Stock % =
ROUND(
    DIVIDE(
        CALCULATE(COUNTROWS(books_data), books_data[Availability] = "In stock"),
        COUNTROWS(books_data)
    ) * 100, 2
)

Average Price by Rating =
AVERAGEX(
    FILTER(
        ALLSELECTED(books_data),
        books_data[Rating] = MAX(books_data[Rating])
    ),
    books_data[Price_USD]
)
```

---

## 📊 Visualizations

### 🔹 KPI Cards

* **Total Books**
* **Average Price (USD)**
* **% In Stock**

### 🔹 Charts

1. **Bar Chart** : Average Price by Rating (X = Rating, Y = Avg Price)
2. **Pie Chart** : Stock Status (In Stock vs Out of Stock)
3. **Donut Chart** : Price Category (Budget / Standard / Premium)

### 🔹 Table View

Displays:

* Title
* Price (USD)
* Rating
* Availability
* Price Category

#### Conditional Formatting:

* `Price_USD > 66`: Highlight with **gold**
* `Rating <= 2`: Highlight with **red background/font**

---

## 🎛️ Filters and Slicers

* **Rating** (1–5)
* **Availability** (In Stock / Out of Stock)
* **Price Category** (Budget / Standard / Premium)
* **Price Range Slider**

---

## 🔍 Drill-Through

Users can **right-click** on any price category in the donut chart to drill into a detail page showing book-level information for that category.

---

## 🧪 Testing and Verification

* ✅ Data Loaded Correctly
* ✅ Prices converted from GBP to USD
* ✅ Conditional formatting applied
* ✅ Filters working as expected
* ✅ Measures & Visuals update dynamically

---

## 🔄 Maintenance

### Refresh Data

* Click **Refresh** in Power BI to update with new book data

### Edit Values

* In Power Query, use "Replace Values" or "Transform" to edit a cell or column

---

## 🚀 Exporting

1. Right-click any visual > **Export Data**
2. Choose summarized or underlying data (CSV/Excel)

---

## 🛠️ Tech Stack

* Power BI Desktop
* DAX (for measures & calculated columns)
* Power Query M (for transformation)
* CSV (as data source)

---

## 📌 Notes

* Currency conversion rate used: **£1 = $1.32**
* Price category thresholds:
  * Budget: <$26.40
  * Standard: $26.40–$66
  * Premium: >$66

---

## 📁 File Structure (Example)

```
├── README.md
├── scrapping/
│   └── raw_data/
│       └── books_data.csv
└── visualization/
│   └──books_visualize_data.pbix
```

---

## 👩‍💻 Author

*Created by Puneeth Kumar for Power BI Book Analysis Project*
