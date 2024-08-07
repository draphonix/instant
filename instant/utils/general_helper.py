class GeneralHelper:
    @staticmethod
    def select_option(options: list) -> str:
        """Select an option from a list of options provided by the user."""
        if not options:
            print("No options available for selection.")
            exit(1)

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        selection = int(input("Select an option: "))
        selected_option = options[selection - 1]
        return selected_option