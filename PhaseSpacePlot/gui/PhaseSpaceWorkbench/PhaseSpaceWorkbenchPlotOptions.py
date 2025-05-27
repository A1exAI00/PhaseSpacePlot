import dearpygui.dearpygui as dpg

#########################################################################################

class PhaseSpaceWorkbenchPlotOptions:
    def setup_plot_options_window(self):
        with dpg.window(label='Plot Options', tag="plot_options_window", pos=(300, 0)):

            # Create two combo boxes to choose axis labels
            dpg.add_combo(label="X Axis Label", tag="x_axis_label",
                        default_value=self.x_axis_label_default, 
                        items=self.axis_posible_labels, 
                        callback=self.callback_change_axis_label, 
                        width=self.plot_options_option_width)
            dpg.add_combo(label="Y Axis Label", tag="y_axis_label",
                        default_value=self.y_axis_label_default, 
                        items=self.axis_posible_labels, 
                        callback=self.callback_change_axis_label,
                        width=self.plot_options_option_width)
        return
    
    def delete_plot_options_window(self):
        dpg.delete_item("plot_options_window")
        return

    def callback_change_axis_label(self, sender, app_data):
        # Update axis labels and consider them to know what to plot
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()
        dpg.configure_item('x_axis', label=x_axis_label)
        dpg.configure_item('y_axis', label=y_axis_label)

        # Redraw every trajectory and dragpoint because of new axis
        for (n,trajectory) in self.trajectories.items():
            curr_sol = trajectory.sol
            curr_t_sol = trajectory.t_sol
            if x_axis_i == len(self.app.variable_names):
                new_x_dragpoint = 0.0
                x_axis_data = curr_t_sol
            else:
                x_axis_data = curr_sol[x_axis_i]
                new_x_dragpoint = x_axis_data[0]

            if y_axis_i == len(self.app.variable_names):
                new_y_dragpoint = 0.0
                y_axis_data = curr_t_sol
            else:
                y_axis_data = curr_sol[y_axis_i]
                new_y_dragpoint = y_axis_data[0]
            dpg.set_value(f"dragpoint_{n}", [new_x_dragpoint, new_y_dragpoint])
            dpg.set_value(f"plot{n}", [x_axis_data, y_axis_data])
        return 