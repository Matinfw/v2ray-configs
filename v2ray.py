name: Collect and Update VLESS/Hysteria2 Configs

on:
  push:
    branches:
      - main 
    paths:
      - 'telegram_config_collector.py' # اگر مسیر فایل پایتون متفاوت است، آن را اینجا مشخص کنید
  schedule:
    - cron: '0 */3 * * *' # هر 6 ساعت یکبار اجرا شود (مثلاً در دقیقه 0 از هر 6 ساعت)
  workflow_dispatch: # اجازه اجرای دستی Workflow از تب Actions

jobs:
  collect_configs:
    runs-on: ubuntu-latest # یا یک image دیگر اگر نیاز دارید

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.x' # از نسخه پایتون مناسب استفاده کنید

    - name: Install dependencies
      run: |
        pip install telethon pycountry ip2geotools

    - name: Cache Telegram session
      uses: actions/cache@v4
      with:
        path: telegram_session.session # نام فایل session تلگرام که در کد پایتون استفاده شده
        key: ${{ runner.os }}-telethon-session-${{ hashFiles('telegram_config_collector.py') }} # کلید cache برای تشخیص تغییر در اسکریپت

    - name: Run config collector script
      env:
        TELEGRAM_API_ID: ${{ secrets.TELEGRAM_API_ID }}
        TELEGRAM_API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
        TELEGRAM_PHONE: ${{ secrets.TELEGRAM_PHONE }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} # GitHub's built-in token often works
      run: |
        python telegram_config_collector.py

    
