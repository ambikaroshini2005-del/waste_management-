# 📊 TrashNet Dataset

## Directory Structure Created ✅

```
dataset-resized/
├── cardboard/   (Empty - Ready for images)
├── glass/       (Empty - Ready for images)
├── metal/       (Empty - Ready for images)
├── paper/       (Empty - Ready for images)
├── plastic/     (Empty - Ready for images)
└── trash/       (Empty - Ready for images)
```

---

## 📥 How to Populate the Dataset

### Step 1: Download from Kaggle
1. Go to: https://www.kaggle.com/datasets/feyzazkefe/trashnet/data
2. Click **"Download"** button
3. Wait for the ZIP file to download (will take a few minutes)

### Step 2: Extract the Files
1. Extract the downloaded ZIP file
2. You should see a folder named `dataset-resized/` inside

### Step 3: Copy Images to Project
Copy all image files from the downloaded `dataset-resized/` folders into the corresponding folders here:

```
Downloaded Files:
└── dataset-resized/
    ├── cardboard/*.jpg    → Copy to ./cardboard/
    ├── glass/*.jpg        → Copy to ./glass/
    ├── metal/*.jpg        → Copy to ./metal/
    ├── paper/*.jpg        → Copy to ./paper/
    ├── plastic/*.jpg      → Copy to ./plastic/
    └── trash/*.jpg        → Copy to ./trash/
```

---

## 📊 Expected Image Count

| Category | Images |
|----------|--------|
| Cardboard | 403 |
| Glass | 686 |
| Metal | 411 |
| Paper | 569 |
| Plastic | 372 |
| Trash | 86 |
| **TOTAL** | **2,527** |

---

## ✅ Verify Installation

Once all images are copied, the application will automatically use them for:
- ✓ Training the ML model
- ✓ Making waste predictions
- ✓ Waste classification

---

## 🔗 Dataset Information

- **Name**: TrashNet
- **Source**: Kaggle (Open-source)
- **Format**: JPG images
- **Resolution**: 128×128 pixels
- **License**: Check Kaggle page for terms

---

**Note**: The application can run without this dataset using mock predictions, but having the actual images enables proper ML model training.
