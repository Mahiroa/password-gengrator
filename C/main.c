#include <windows.h>
#include <commctrl.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#include "tinyexpr.h"

#pragma comment(lib, "comctl32.lib")

#define IDC_EXPRESSION_EDIT 101
#define IDC_LENGTH_EDIT     102
#define IDC_LENGTH_SLIDER   103
#define IDC_UPPER_CHECK     104
#define IDC_LOWER_CHECK     105
#define IDC_SPECIAL_CHECK   106
#define IDC_GENERATE_BUTTON 107
#define IDC_COPY_BUTTON     108

typedef struct {
    HWND hTimeLabel;
    HWND hExpressionEdit;
    HWND hLengthEdit;
    HWND hLengthSlider;
    HWND hUpperCheck;
    HWND hLowerCheck;
    HWND hSpecialCheck;
    HWND hResultEdit;

    int length;
    BOOL includeUpper;
    BOOL includeLower;
    BOOL includeSpecial;
    char expression[256];
    char result[1024];
} AppState;

void GenerateString(HWND hwnd, AppState* state) {
    time_t now = time(NULL);
    struct tm* tm = localtime(&now);
    char timeStr[256];
    strftime(timeStr, sizeof(timeStr), "种子生成时间：%Y-%m-%d %H:%M:%S", tm);
    SetWindowText(state->hTimeLabel, timeStr);

    double total_seconds = tm->tm_hour * 3600 + tm->tm_min * 60 + tm->tm_sec;
    double hours = tm->tm_hour;
    double minutes = tm->tm_min;
    double seconds = tm->tm_sec;

    te_variable vars[] = {
        {"total_seconds", &total_seconds},
        {"hours", &hours},
        {"minutes", &minutes},
        {"seconds", &seconds},
        {"cos", (const void*)cos, TE_FUNCTION1},
        {"sin", (const void*)sin, TE_FUNCTION1},
        {"tan", (const void*)tan, TE_FUNCTION1}
    };

    int error;
    te_expr* expr = te_compile(state->expression, vars, sizeof(vars)/sizeof(vars[0]), &error);
    if (!expr) {
        MessageBox(hwnd, "无效的数学表达式", "错误", MB_ICONERROR);
        return;
    }

    double seed = fabs(te_eval(expr));
    te_free(expr);
    srand((unsigned int)(seed * 1000000));

    char pool[256] = {0};
    if (state->includeUpper) strcat(pool, "ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    if (state->includeLower) strcat(pool, "abcdefghijklmnopqrstuvwxyz");
    if (state->includeSpecial) strcat(pool, "!@#$%^&*()_+-=[]{}|;:',.<>?/`~");

    if (strlen(pool) == 0) {
        MessageBox(hwnd, "至少需要选择一种字符类型", "错误", MB_ICONERROR);
        return;
    }

    int poolLen = (int)strlen(pool);
    int length = state->length;
    if (length < 1) {
        MessageBox(hwnd, "长度必须大于0", "错误", MB_ICONERROR);
        return;
    }

    char* buf = (char*)malloc(length + 1);
    for (int i = 0; i < length; i++) {
        buf[i] = pool[rand() % poolLen];
    }
    buf[length] = '\0';
    strncpy(state->result, buf, sizeof(state->result));
    free(buf);

    SetWindowText(state->hResultEdit, state->result);
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static AppState* state;

    switch (msg) {
        case WM_CREATE: {
            INITCOMMONCONTROLSEX icc = {sizeof(icc), ICC_WIN95_CLASSES};
            InitCommonControlsEx(&icc);

            state = (AppState*)malloc(sizeof(AppState));
            memset(state, 0, sizeof(AppState));
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)state);

            state->length = 12;
            state->includeUpper = TRUE;
            state->includeLower = TRUE;
            strcpy(state->expression, "cos(total_seconds)");

            // 创建控件
            state->hTimeLabel = CreateWindow("STATIC", "种子生成时间：",
                WS_CHILD | WS_VISIBLE | SS_LEFT,
                20, 20, 300, 20, hwnd, NULL, NULL, NULL);

            state->hExpressionEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", state->expression,
                WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                20, 50, 380, 24, hwnd, (HMENU)IDC_EXPRESSION_EDIT, NULL, NULL);

            state->hLengthEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "12",
                WS_CHILD | WS_VISIBLE | ES_NUMBER,
                20, 80, 60, 24, hwnd, (HMENU)IDC_LENGTH_EDIT, NULL, NULL);

            state->hLengthSlider = CreateWindow(TRACKBAR_CLASS, NULL,
                WS_CHILD | WS_VISIBLE | TBS_AUTOTICKS | TBS_HORZ,
                90, 80, 310, 30, hwnd, (HMENU)IDC_LENGTH_SLIDER, NULL, NULL);
            SendMessage(state->hLengthSlider, TBM_SETRANGE, TRUE, MAKELONG(1, 100));
            SendMessage(state->hLengthSlider, TBM_SETPOS, TRUE, 12);

            state->hUpperCheck = CreateWindow("BUTTON", "大写字母",
                WS_CHILD | WS_VISIBLE | BS_CHECKBOX,
                20, 110, 100, 24, hwnd, (HMENU)IDC_UPPER_CHECK, NULL, NULL);
            SendMessage(state->hUpperCheck, BM_SETCHECK, BST_CHECKED, 0);

            state->hLowerCheck = CreateWindow("BUTTON", "小写字母",
                WS_CHILD | WS_VISIBLE | BS_CHECKBOX,
                130, 110, 100, 24, hwnd, (HMENU)IDC_LOWER_CHECK, NULL, NULL);
            SendMessage(state->hLowerCheck, BM_SETCHECK, BST_CHECKED, 0);

            state->hSpecialCheck = CreateWindow("BUTTON", "特殊字符",
                WS_CHILD | WS_VISIBLE | BS_CHECKBOX,
                240, 110, 100, 24, hwnd, (HMENU)IDC_SPECIAL_CHECK, NULL, NULL);

            state->hResultEdit = CreateWindowEx(WS_EX_CLIENTEDGE, "EDIT", "",
                WS_CHILD | WS_VISIBLE | ES_READONLY,
                20, 140, 380, 24, hwnd, NULL, NULL, NULL);

            CreateWindow("BUTTON", "重新生成",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                20, 170, 80, 24, hwnd, (HMENU)IDC_GENERATE_BUTTON, NULL, NULL);

            CreateWindow("BUTTON", "复制到剪贴板",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                110, 170, 120, 24, hwnd, (HMENU)IDC_COPY_BUTTON, NULL, NULL);

            GenerateString(hwnd, state);
            break;
        }

        case WM_COMMAND: {
            state = (AppState*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
            int id = LOWORD(wParam);
            int code = HIWORD(wParam);

            if (id == IDC_EXPRESSION_EDIT && code == EN_CHANGE) {
                GetWindowText(state->hExpressionEdit, state->expression, 256);
                GenerateString(hwnd, state);
            }
            else if (id == IDC_LENGTH_EDIT && code == EN_CHANGE) {
                char buf[32];
                GetWindowText(state->hLengthEdit, buf, 32);
                int len = atoi(buf);
                if (len > 0 && len <= 100) {
                    state->length = len;
                    SendMessage(state->hLengthSlider, TBM_SETPOS, TRUE, len);
                    GenerateString(hwnd, state);
                }
            }
            else if (id == IDC_UPPER_CHECK) {
                state->includeUpper = SendMessage(state->hUpperCheck, BM_GETCHECK, 0, 0) == BST_CHECKED;
                GenerateString(hwnd, state);
            }
            else if (id == IDC_LOWER_CHECK) {
                state->includeLower = SendMessage(state->hLowerCheck, BM_GETCHECK, 0, 0) == BST_CHECKED;
                GenerateString(hwnd, state);
            }
            else if (id == IDC_SPECIAL_CHECK) {
                state->includeSpecial = SendMessage(state->hSpecialCheck, BM_GETCHECK, 0, 0) == BST_CHECKED;
                GenerateString(hwnd, state);
            }
            else if (id == IDC_GENERATE_BUTTON) {
                GenerateString(hwnd, state);
            }
            else if (id == IDC_COPY_BUTTON) {
                if (OpenClipboard(hwnd)) {
                    EmptyClipboard();
                    HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, strlen(state->result) + 1);
                    if (hMem) {
                        char* pMem = (char*)GlobalLock(hMem);
                        strcpy(pMem, state->result);
                        GlobalUnlock(hMem);
                        SetClipboardData(CF_TEXT, hMem);
                    }
                    CloseClipboard();
                    MessageBox(hwnd, "已复制到剪贴板", "成功", MB_ICONINFORMATION);
                }
            }
            break;
        }

        case WM_HSCROLL: {
            state = (AppState*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
            if ((HWND)lParam == state->hLengthSlider) {
                int pos = (int)SendMessage(state->hLengthSlider, TBM_GETPOS, 0, 0);
                if (pos != state->length) {
                    state->length = pos;
                    char buf[32];
                    sprintf(buf, "%d", pos);
                    SetWindowText(state->hLengthEdit, buf);
                    GenerateString(hwnd, state);
                }
            }
            break;
        }

        case WM_CLOSE:
            DestroyWindow(hwnd);
            break;

        case WM_DESTROY:
            free(state);
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    WNDCLASSEX wc = {
        .cbSize = sizeof(WNDCLASSEX),
        .style = CS_HREDRAW | CS_VREDRAW,
        .lpfnWndProc = WndProc,
        .hInstance = hInstance,
        .hCursor = LoadCursor(NULL, IDC_ARROW),
        .hbrBackground = (HBRUSH)(COLOR_WINDOW+1),
        .lpszClassName = "RandomStringGenerator"
    };

    if (!RegisterClassEx(&wc)) {
        MessageBox(NULL, "窗口注册失败", "错误", MB_ICONERROR);
        return 0;
    }

    HWND hwnd = CreateWindowEx(0, "RandomStringGenerator", "随机字符串生成器",
        WS_OVERLAPPEDWINDOW & ~WS_THICKFRAME & ~WS_MAXIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 430, 220, NULL, NULL, hInstance, NULL);

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}