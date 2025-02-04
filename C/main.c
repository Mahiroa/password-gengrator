#include <windows.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>

// 窗口过程函数
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

// 定义窗口类名称
const char CLASS_NAME[] = "RandomStringGenerator";

// 生成随机字符串
void GenerateRandomString(HWND hwnd) {
    char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:',.<>?/`~";
    const int charsetLength = strlen(charset);
    int length = 12; // 默认长度
    char result[128] = {0};

    // 使用当前时间作为随机种子
    srand((unsigned int)time(NULL));

    for (int i = 0; i < length; i++) {
        result[i] = charset[rand() % charsetLength];
    }

    // 显示生成的字符串
    SetWindowTextA(GetDlgItem(hwnd, 104), result);
}

// 主函数
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {
    // 注册窗口类
    const WNDCLASS wc = {
        .style = CS_HREDRAW | CS_VREDRAW,
        .lpfnWndProc = WindowProc,
        .hInstance = hInstance,
        .lpszClassName = CLASS_NAME,
    };

    RegisterClass(&wc);

    // 创建窗口
    HWND hwnd = CreateWindowEx(
        0,                              // 扩展窗口样式
        CLASS_NAME,                     // 窗口类名
        "随机字符串生成器",              // 窗口标题
        WS_OVERLAPPEDWINDOW,            // 窗口样式
        CW_USEDEFAULT, CW_USEDEFAULT,   // 初始位置
        400, 200,                       // 窗口宽度和高度
        NULL,                           // 父窗口
        NULL,                           // 菜单
        hInstance,                      // 应用程序实例
        NULL                            // 附加参数
    );

    if (hwnd == NULL) {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);

    // 消息循环
    MSG msg = {0};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

// 窗口过程函数
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_CREATE: {
            // 创建控件
            CreateWindow("STATIC", "当前时间：", WS_CHILD | WS_VISIBLE | SS_LEFT, 10, 10, 200, 20, hwnd, (HMENU)101, NULL, NULL);
            CreateWindow("EDIT", "12", WS_CHILD | WS_VISIBLE | WS_BORDER, 10, 40, 50, 20, hwnd, (HMENU)102, NULL, NULL);
            CreateWindow("BUTTON", "生成", WS_CHILD | WS_VISIBLE | WS_TABSTOP, 70, 40, 80, 20, hwnd, (HMENU)103, NULL, NULL);
            CreateWindow("STATIC", "", WS_CHILD | WS_VISIBLE | WS_BORDER, 10, 70, 300, 20, hwnd, (HMENU)104, NULL, NULL);

            // 初始化随机字符串
            GenerateRandomString(hwnd);
            break;
        }

        case WM_COMMAND: {
            // 按钮点击事件
            if (LOWORD(wParam) == 103) {
                GenerateRandomString(hwnd);
            }
            break;
        }

        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;

        default:
            return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }

    return 0;
}