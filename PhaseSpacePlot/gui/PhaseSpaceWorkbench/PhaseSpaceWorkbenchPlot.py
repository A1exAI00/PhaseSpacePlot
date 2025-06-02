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
                for (n,trajectory) in self.dragpoint_trajectories.items():
                    dpg.add_drag_point(label=f"Init. State {n}", tag=f"dragpoint_{n}", 
                                    callback=self.callback_change_dragpoint_position,
                                    user_data={"n":n},
                                    color=[255, 0, 0, 150])
                    dpg.add_line_series([], [], label="", parent='y_axis', tag=f"dragpoint_plot_{n}")
                
                # Add plot for every near SoE init state
                for (n,trajectory) in self.near_SoE_trajectories.items():
                    dpg.add_line_series([], [], label="", parent='y_axis', tag=f"near_SoE_plot_{n}")

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