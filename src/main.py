from controller import Controller
from views.app import App


def main():

    app = App()

    controller = Controller(app)

    app.mainloop()


if __name__ == "__main__":
    main()
