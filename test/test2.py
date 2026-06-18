import csv
import os

def init_csv(filename="score_table.csv"):
    """初始化 CSV 檔案，單純寫入第一行的標題欄位"""
    headers = ["學校", "學系", "國文", "數學A", "數學B", "英文", "自然", "社會"]

    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)  # 只寫入第一行標題

    # print(f"【成功】已建立全新 CSV 檔案：{filename}")


def fill_grades_csv(school_name, department, subjects, grades, filename="score_table.csv"):
    """
    輸入學校名稱、科目 list、等第 list。
    自動在 CSV 結尾新增一行，並把等第填入對應的科目下方。
    """
    if not os.path.exists(filename):
        print(f"錯誤：找不到檔案 {filename}，正在自動為您初始化...")
        init_csv(filename)

    # 1. 讀取現有的 CSV 所有內容
    with open(filename, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("錯誤：檔案完全空白，請先執行 init_csv()")
        return

    headers = rows[0]  # 第一行永遠是標題：['學系/科目', '國文', '數學A', ...]

    # 2. 建立新的一列資料，預設全部留空
    # 長度與標題一樣長，例如：['', '', '', '', '', '', '']
    new_row = [""] * len(headers)

    # 將第一格（學系/科目）填入你指定的學校名稱
    new_row[0] = school_name
    new_row[1] = department

    # 3. 偵測並比對兩組 list
    for sub, grade in zip(subjects, grades):
        if sub in headers:
            col_idx = headers.index(sub)  # 找到科目所在的直欄編號
            new_row[col_idx] = grade  # 把等第填入該位置
            print(f"[{school_name}] 成功對應：【{sub}】填入 -> {grade}")
        else:
            print(f"[{school_name}] 跳過：標題中沒有【{sub}】這個科目。")

    # 4. 將這一行新資料追加（Append）到原本的 rows 裡面
    rows.append(new_row)

    # 5. 寫回 CSV 檔案
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"【成功】{school_name} 的資料已寫入 {filename}！\n")

if __name__ == "__main__":
    init_csv("my_report.csv")  # 確保 CSV 檔案存在且有正確的標題
    # 測試用：模擬填入一筆資料
    for i in range(3):
        fill_grades_csv(
            school_name="國立台灣大學",
            department="資訊工程學系",
            subjects=["國文", "數學A", "英文"],
            grades=["甲等", "乙等", "甲等"],
            filename="my_report.csv"
        )