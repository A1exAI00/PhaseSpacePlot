import dearpygui.dearpygui as dpg

#########################################################################################

class PhaseSpaceWorkbenchPlot:
    def setup_phase_space_plot_window(self):
        with dpg.window(label='Phase Space Plot', tag="plot_window", pos=(750, 0)):
            with dpg.plot(label='', tag="phase_space_plot", width=700, height=700):

                # Add x and y axis
                dpg.add_plot_axis(dpg.mvXAxis, 
                                label=self.x_axis_label_default, tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, 
                                label=self.y_axis_label_default, tag="y_axis")

                # Add dragpoint and plot for every trajectory
                for (n,trajectory) in self.trajectories.items():
                    dpg.add_drag_point(label=f"Init. State {n}", tag=f"dragpoint_{n}", 
                                    callback=self.callback_change_dragpoint_position,
                                    color=[255, 0, 0, 150])
                    dpg.add_line_series([], [], label="", parent='y_axis', tag=f"plot{n}")

        # Refresh all trajectories
        self.callback_change_parameter(None, None)
        return
    
    def delete_phase_space_plot_window(self):
        dpg.delete_item("plot_window")

    def get_axis_labels(self):
        x_axis_label = dpg.get_value("x_axis_label")
        y_axis_label = dpg.get_value("y_axis_label")
        x_axis_i = self.axis_posible_labels.index(x_axis_label)
        y_axis_i = self.axis_posible_labels.index(y_axis_label)
        return (x_axis_label, y_axis_label, x_axis_i, y_axis_i)

    def update_from_trajectory_to_plot(self, n):
        _, _, x_axis_i, y_axis_i = self.get_axis_labels()

        sol, t_sol = self.trajectories[n].sol, self.trajectories[n].t_sol
        if x_axis_i == len(self.app.variable_names):
            x_axis_data = t_sol
        else:
            x_axis_data = sol[x_axis_i]

        if y_axis_i == len(self.app.variable_names):
            y_axis_data = t_sol
        else:
            y_axis_data = sol[y_axis_i]
        dpg.set_value(f"plot{n}", [x_axis_data, y_axis_data])
        return

    def callback_change_dragpoint_position(self, sender, app_data):
        n = int(dpg.get_item_configuration(sender)["label"][len("Init. State "):])
        self.update_from_dragpoint_to_dragpoint_table(n)
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_dragpoint_table_to_trajectory(n)
        self.update_from_trajectory_to_plot(n)
        return