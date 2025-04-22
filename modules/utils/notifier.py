from win10toast import ToastNotifier

toast = ToastNotifier()

def notify(title : str, message:str, duration=10):
    toast.show_toast(
        title, 
        message, 
        duration=duration, 
        threaded=True
    )