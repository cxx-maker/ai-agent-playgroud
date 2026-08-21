"""项目入口"""
import db
import ui


if __name__ == "__main__":
    db.init_db()
    ui.demo.launch()
