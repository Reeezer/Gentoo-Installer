gray = "e7e7e7"
white = "fff"
light_blue = "E0E6F4"
blue = "7994DE"
black = "333333"

styles = """
    Window {
        background-color: #e7e7e7;
        color: #333333;
    }
    
    QWidget#category, QWidget#leftPane {
        border-radius: 8px; 
        background-color: #fff;
    }
    
    QWidget#preference {
        background-color: #f00;
    }

    QPushButton { 
        background-color: #E0E6F4; 
        color: #7994DE; 
        border-radius: 8px; 
        padding: 4px;
    }
    
    QPushButton:hover { 
        background-color: #7994DE; 
        color: #fff; 
    }
 
    SideBar { 
        border-radius: 4px; 
        background-color: #e7e7e7; 
        padding: 4px; 
        color: #333333;
    }
    
    QListWidget::item:hover {
        background-color: #E0E6F4;
        color: #7994DE;
        border-radius: 4px; 
    }
    
    QListWidget::item:selected {
        background-color: #7994DE; 
        color: #fff; 
        border-radius: 4px; 
    }
    
    QLineEdit {
        background-color: #e7e7e7; 
        color: #333333; 
        border-radius: 4px; 
        padding: 4px;
    }
    
    QLabel {
        color: #333333; 
    }
"""