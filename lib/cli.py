import util.helpers as util

if __name__ == "__main__":

    while util.menu_reset["operation"] is False:
        util.perform_operation("select_operation")
        util.clear_selected_values()
