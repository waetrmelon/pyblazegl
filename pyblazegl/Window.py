from ctypes import *
from ctypes.wintypes import *
import ctypes

gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32

windll.user32.DefWindowProcW.argtypes = HWND, UINT, WPARAM, LPARAM
WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)
WS_EX_APPWINDOW = 0x40000
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_CAPTION = 0xc00000
SW_SHOWNORMAL = 1
SW_SHOW = 5
CS_HREDRAW = 2
CS_VREDRAW = 1
CW_USEDEFAULT = 0x80000000
WM_DESTROY = 2
WHITE_BRUSH = 0

class WNDCLASSEX(Structure):
    _fields_ = [("cbSize", c_uint),
                ("style", c_uint),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", c_int),
                ("cbWndExtra", c_int),
                ("hInstance", HANDLE),
                ("hIcon", HANDLE),
                ("hCursor", HANDLE),
                ("hBrush", HANDLE),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR),
                ("hIconSm", HANDLE)]

def PyWndProcedure(hWnd, Msg, wParam, lParam):
    if Msg == WM_DESTROY:
        windll.user32.PostQuitMessage(0)
    else:
        return windll.user32.DefWindowProcW(hWnd, Msg, wParam, lParam)
    return 0

class WindowContext():
    def __init__(self,name,width,height) -> None:
        self.name = name
        self.width = width
        self.height = height

        WndProc = WNDPROCTYPE(PyWndProcedure)
        hInst = windll.kernel32.GetModuleHandleW(0)
        wclassName = 'pyblazegl-class'
        
        wndClass = WNDCLASSEX()
        wndClass.cbSize = sizeof(WNDCLASSEX)
        wndClass.style = CS_HREDRAW | CS_VREDRAW
        wndClass.lpfnWndProc = WndProc
        wndClass.cbClsExtra = 0
        wndClass.cbWndExtra = 0
        wndClass.hInstance = hInst
        wndClass.hIcon = 0
        wndClass.hCursor = 0
        wndClass.hBrush = windll.gdi32.GetStockObject(WHITE_BRUSH)
        wndClass.lpszMenuName = 0
        wndClass.lpszClassName = wclassName
        wndClass.hIconSm = 0
        
        regRes = windll.user32.RegisterClassExW(byref(wndClass))
        
        self.hWnd = windll.user32.CreateWindowExW(
        0,wclassName,self.name,
        WS_OVERLAPPEDWINDOW | WS_CAPTION,
        CW_USEDEFAULT, CW_USEDEFAULT,
        self.width,self.height,0,0,hInst,0)
        
        if not self.hWnd:
            raise Exception('Failed to create window successfully!')

        self.SetBackground((255,0,0))
        print('ShowWindow', windll.user32.ShowWindow(self.hWnd, SW_SHOW))
        print('UpdateWindow', windll.user32.UpdateWindow(self.hWnd))
        
        msg = MSG()
        lpmsg = pointer(msg)

        print('loop')
        while windll.user32.GetMessageA(lpmsg, 0, 0, 0) != 0:
            windll.user32.TranslateMessage(lpmsg)
            windll.user32.DispatchMessageA(lpmsg)

        print('finished')
    def SetBackground(self, colour):
        new_bg_color = RGB(colour[0], colour[1], colour[2]) 
        hBrush = gdi32.CreateSolidBrush(new_bg_color)

        # Update the background brush of the window's class
        class_atom = user32.GetClassLongPtrW(self.hWnd, -16)  # GCL_HMODULE
        user32.SetClassLongPtrW(self.hWnd, -10, hBrush)

        # Invalidate the window to trigger a redraw
        user32.InvalidateRect(self.hWnd, None, True)
        user32.UpdateWindow(self.hWnd)
        windll.user32.UpdateWindow(self.hWnd)
            

def CreateWindow(name="pyblazegl-application", width=800, height=600): 
    return WindowContext(name,width,height)