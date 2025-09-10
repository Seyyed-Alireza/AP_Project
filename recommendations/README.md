# Simple Recommendation System

این یک سیستم توصیه ساده شده است که شامل دو الگوریتم اصلی فیلترینگ مشارکتی می‌باشد:

## الگوریتم‌های پیاده‌سازی شده

### 1. UBCF (User-Based Collaborative Filtering)
- **فیلترینگ مشارکتی مبتنی بر کاربر**
- محاسبه ماتریس شباهت کاربر-کاربر با استفاده از شباهت کسینوسی
- پیش‌بینی امتیاز بر اساس کاربران مشابه
- ارائه توصیه‌های شخصی‌سازی شده با دلایل

### 2. IBCF (Item-Based Collaborative Filtering)
- **فیلترینگ مشارکتی مبتنی بر آیتم**
- محاسبه ماتریس شباهت آیتم-آیتم
- پیش‌بینی امتیاز بر اساس محصولات مشابه
- توصیه محصولات مشابه به سلیقه کاربر

## فایل‌های کلیدی

### `engine.py`
- کلاس `RecommendationEngine` با متدهای ساده
- `create_user_item_matrix()`: ایجاد ماتریس کاربر-محصول
- `calculate_user_similarity()`: محاسبه شباهت کاربران
- `calculate_item_similarity()`: محاسبه شباهت محصولات
- `user_based_collaborative_filtering()`: توصیه‌های UBCF
- `item_based_collaborative_filtering()`: توصیه‌های IBCF
- `predict_rating()`: پیش‌بینی امتیاز برای محصول خاص

### `views.py`
- `ubcf_recommendations()`: نمایش توصیه‌های UBCF
- `ibcf_recommendations()`: نمایش توصیه‌های IBCF
- `similarity_matrices_view()`: نمایش ماتریس‌های شباهت
- `predict_rating_api()`: API پیش‌بینی امتیاز
- `cf_dashboard()`: داشبورد اصلی

### Templates
- `ubcf.html`: صفحه نمایش توصیه‌های UBCF
- `ibcf.html`: صفحه نمایش توصیه‌های IBCF
- `cf_dashboard.html`: داشبورد اصلی سیستم
- `similarity_matrices.html`: نمایش ماتریس‌های شباهت

## ویژگی‌های کلیدی

1. **محاسبه ماتریس‌های شباهت**: استفاده از شباهت کسینوسی
2. **پیش‌بینی امتیاز**: برای هر دو الگوریتم UBCF و IBCF
3. **ارائه دلایل**: توضیح چرایی هر توصیه
4. **رابط کاربری ساده**: طراحی تمیز و قابل فهم
5. **API endpoints**: برای استفاده از سایر بخش‌های سیستم

## نحوه استفاده

1. بروید به `/recommendations/` برای مشاهده داشبورد
2. انتخاب کنید بین UBCF یا IBCF
3. مشاهده توصیه‌ها با امتیازات پیش‌بینی شده و دلایل
4. مشاهده ماتریس‌های شباهت در بخش ابزارهای تحلیلی

## وابستگی‌ها

- Django
- pandas
- numpy  
- scikit-learn (اختیاری - در صورت عدم وجود از محاسبات دستی استفاده می‌شود)

## URL Patterns

```
/recommendations/                    # داشبورد اصلی
/recommendations/ubcf/              # توصیه‌های UBCF  
/recommendations/ibcf/              # توصیه‌های IBCF
/recommendations/similarity-matrices/ # ماتریس‌های شباهت
/recommendations/api/predict-rating/<id>/ # API پیش‌بینی امتیاز
```
