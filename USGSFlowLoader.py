from urllib.request import urlopen
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Scrollbar
from tkinter.ttk import Progressbar
import os, textwrap, time, sys
from dateutil.parser import parse

# to build application...
# cd to directory, then: pyinstaller --onefile --noconsole USGSFlowLoader.py

class FlowLoader():
    """An application to download daily stream flow data from the USGS."""
    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(False,False)
        self.window.title("USGS Flow Loader")
        self.work_dir = ""
        self.in_file = tk.StringVar()
        self.in_file_data = []
        self.input_delimiter_str = tk.StringVar(value = '","')
        self.headers_check_var = tk.IntVar(value=1)
        self.manual_id_str = tk.StringVar()
        self.manual_name_str = tk.StringVar()
        self.station_id = []
        self.station_name = []
        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self.convert_str = tk.StringVar()
        self.convert_vals = ["ft³/s","m³/s","mm³/s"]
        self.output_formats = [".csv",".txt"]
        self.output_delimiter_str = tk.StringVar(value = '","')
        self.output_data = []
        self.running = False
    
    def launch(self):
        """Open the Flow Loader GUI"""
        pad=5
        self.station_labelframe = tk.LabelFrame(self.window,text="Select Stations")
        self.station_labelframe.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.N)
        self.station_notebook = ttk.Notebook(self.station_labelframe)
        self.station_notebook.grid()
        self.file_panel = tk.Frame(self.station_notebook)
        self.file_panel.grid()
        self.manual_panel = tk.Frame(self.station_notebook)
        self.manual_panel.grid()
        self.station_notebook.add(self.file_panel,text="From File")
        self.station_notebook.add(self.manual_panel,text="Enter Manually")

        self.file_select_frame = tk.Frame(self.file_panel)
        self.file_select_frame.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.file_select_label = tk.Label(self.file_select_frame,text="File (.csv or .txt):     ")
        self.file_select_label.grid(row = 0, column = 0,padx=pad,pady=pad)
        self.file_select_entry = ttk.Entry(self.file_select_frame,textvariable=self.in_file,justify="right",width=49)
        self.file_select_entry.grid(row=0,column=1,padx=pad,pady=pad)
        self.choose_file_button = ttk.Button(self.file_select_frame,text="...",width=4,command=self.choose_file)
        self.choose_file_button.grid(row=0,column=2,padx=pad,pady=pad)
        self.delim_header_frame = tk.Frame(self.file_panel)
        self.delim_header_frame.grid(row=1,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.input_delim_label = tk.Label(self.delim_header_frame,text="Input Delimiter:      ")
        self.input_delim_label.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.input_delim_entry = ttk.Entry(self.delim_header_frame,textvariable=self.input_delimiter_str,justify="right",width=10)
        self.input_delim_entry.grid(row=0,column=1,padx=pad,pady=pad,sticky=tk.W)
        self.input_delim_space = tk.Label(self.delim_header_frame,text="")
        self.input_delim_space.grid(row=0,column=2,padx=pad*6+1,pady=pad,sticky=tk.W)
        self.header_check_label = tk.Label(self.delim_header_frame,text="Does file have headers?")
        self.header_check_label.grid(row=0,column=3,padx=pad,pady=pad,sticky=tk.W)
        self.headers_check = tk.Checkbutton(self.delim_header_frame,variable = self.headers_check_var) 
        self.headers_check.grid(row = 0, column = 4,padx=pad,pady=pad, sticky = tk.W)
        self.id_select_frame = tk.Frame(self.file_panel)
        self.id_select_frame.grid(row=2,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.id_select_label = tk.Label(self.id_select_frame,text="Station ID Field:      ")
        self.id_select_label.grid(row = 0, column = 0,padx=pad,pady=pad,sticky=tk.W)
        self.id_select_combo = ttk.Combobox(self.id_select_frame,state="readonly",width = 46)
        self.id_select_combo.grid(row=0,column=1,padx=pad,pady=pad,sticky=tk.W)
        self.name_select_frame = tk.Frame(self.file_panel)
        self.name_select_frame.grid(row=3,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.name_select_label = tk.Label(self.name_select_frame,text="Station Name Field: ")
        self.name_select_label.grid(row = 0, column = 0,padx=pad,pady=pad,sticky=tk.W)
        self.name_select_combo = ttk.Combobox(self.name_select_frame,state="readonly",width = 46)
        self.name_select_combo.grid(row=0,column=1,padx=0,pady=pad,sticky=tk.W)

        self.manual_id_frame = tk.Frame(self.manual_panel)
        self.manual_id_frame.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.manual_id_label = tk.Label(self.manual_id_frame,text="Station IDs:        ")
        self.manual_id_label.grid(row = 0, column = 0,padx=pad,pady=pad)
        self.manual_id_entry = ttk.Entry(self.manual_id_frame,textvariable=self.manual_id_str,justify="right",width=59)
        self.manual_id_entry.grid(row=0,column=1,padx=pad,pady=pad)
        self.manual_name_frame = tk.Frame(self.manual_panel)
        self.manual_name_frame.grid(row=1,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.manual_name_label = tk.Label(self.manual_name_frame,text="Station Names: ")
        self.manual_name_label.grid(row = 1, column = 0,padx=pad,pady=pad)
        self.manual_name_entry = ttk.Entry(self.manual_name_frame,textvariable=self.manual_name_str,justify="right",width=59)
        self.manual_name_entry.grid(row=1,column=1,padx=pad,pady=pad)

        self.settings_labelframe = tk.LabelFrame(self.window,text="Download Settings")
        self.settings_labelframe.grid(row=1,column=0,padx=pad,pady=pad,sticky=tk.N) 
        self.date_frame = tk.Frame(self.settings_labelframe)
        self.date_frame.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.start_date_label = tk.Label(self.date_frame,text="Start Date (yyyy-mm-dd):")
        self.start_date_label.grid(row = 0, column = 0,padx=pad,pady=pad)
        self.start_date_entry = ttk.Entry(self.date_frame,textvariable=self.start_date,justify="right",width=10)
        self.start_date_entry.grid(row=0,column=1,padx=pad,pady=pad,sticky=tk.W)
        self.date_space = tk.Label(self.date_frame,text="")
        self.date_space.grid(row=0,column=2,padx=pad*2,pady=pad)
        self.end_date_label = tk.Label(self.date_frame,text="End Date (yyyy-mm-dd):")
        self.end_date_label.grid(row = 0, column = 3,padx=pad,pady=pad)
        self.end_date_entry = ttk.Entry(self.date_frame,textvariable=self.end_date,justify="right",width=10)
        self.end_date_entry.grid(row=0,column=4,padx=pad,pady=pad,sticky=tk.W)
        self.convert_frame = tk.Frame(self.settings_labelframe)
        self.convert_frame.grid(row=1,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.convert_label = tk.Label(self.convert_frame,text="Conversion:                        ")
        self.convert_label.grid(row=0,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.conversion_combo = ttk.Combobox(self.convert_frame,state="readonly",values=self.convert_vals,width = 7,justify="left")
        self.conversion_combo.grid(row=0,column=1,padx=pad,pady=pad,sticky=tk.W)
        self.conversion_combo.current(0)
        self.output_format_frame = tk.Frame(self.settings_labelframe)
        self.output_format_frame.grid(row=2,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.output_format_file = tk.Label(self.output_format_frame,text="Output Format:                  ")
        self.output_format_file.grid(row = 0, column = 0,padx=pad,pady=pad)
        self.output_format_combo = ttk.Combobox(self.output_format_frame,state="readonly",values=self.output_formats,width = 7,justify="left")
        self.output_format_combo.grid(row=0,column=1,padx=pad,pady=pad,sticky=tk.W)
        self.output_format_combo.current(0)
        self.output_space = tk.Label(self.output_format_frame,text="")
        self.output_space.grid(row=0,column=2,padx=pad*2,pady=pad)
        self.output_delimiter_label = tk.Label(self.output_format_frame,text = "Output Delimiter:             ")
        self.output_delimiter_label.grid(row=0,column=3,padx=pad,pady=pad)
        self.output_delimiter_entry = ttk.Entry(self.output_format_frame,textvariable=self.output_delimiter_str,justify="right",width=10)
        self.output_delimiter_entry.grid(row=0,column=4,padx=pad,pady=pad,sticky=tk.W)

        self.command_labelframe = tk.LabelFrame(self.window,text="Commands")
        self.command_labelframe.grid(row=2,column=0,padx=pad,pady=pad)
        self.text_frame = tk.Frame(self.command_labelframe)
        self.text_frame.grid(row = 0, column = 0, sticky=tk.W)
        self.scroll = Scrollbar(self.text_frame, orient = 'vertical', jump = 0)
        self.scroll.grid(row = 0, column = 2, pady = 0, padx = 0, sticky = 'ns')
        self.text_box = tk.Text(self.text_frame,height = 8, width = 64,state = 'disabled',font = "Times 11", wrap = "word",yscrollcommand = self.scroll.set)
        self.text_box.grid(row=0,column=0,padx=pad,pady=pad)
        self.scroll.config(command = self.text_box.yview)
        self.button_frame = tk.Frame(self.command_labelframe)
        self.button_frame.grid(row=1,column=0,padx=pad,pady=pad,sticky=tk.W)
        self.help_button = ttk.Button(self.button_frame,text="Help",width=6,command=self.open_help)
        self.help_button.grid(row=0,column=0,padx=2,pady=pad)
        self.set_dir_button = ttk.Button(self.button_frame,text="Set Working Directory",command=self.set_work_dir)
        self.set_dir_button.grid(row=0,column=1,padx=2,pady=pad)
        self.open_dir_button = ttk.Button(self.button_frame,text="Open Working Directory",command=self.open_work_dir)
        self.open_dir_button.grid(row=0,column=2,padx=2,pady=pad)
        self.run_button = ttk.Button(self.button_frame,text="Run",width=6,command=self.run)
        self.run_button.grid(row=0,column=3,padx=2,pady=pad)
        self.progbar = Progressbar(self.button_frame, length = 100, mode = 'determinate')
        self.progbar.grid(row = 0, column = 4, padx = 4, pady = pad, sticky = tk.E)

        # resize and reposition window
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = int((ws/2) - 251)
        y = int((hs/2) - 301)
        self.window.geometry(f"503x602+{x}+{y}")

        self.window.mainloop()
    
    def choose_file(self):
        """Choose a file to load station IDs and names."""
        filename = filedialog.askopenfilename(parent = self.window,title = "Select file", filetypes = (("CSV files","*.csv"),("Text files","*.txt"),("all files","*.*"))) #open an existing file
        if len(filename) > 0: #if they didn't press cancel
            self.load_file(filename)
    
    def load_file(self,filename):
        """Load the file and parse the data."""
        try:
            file = open(filename, 'r')
            self.in_file_data = [row.strip().split(self.input_delimiter_str.get()[1:-1]) for row in file.readlines()]
            file.close()
            headers = self.in_file_data[0]
            self.in_file.set(filename)
            self.id_select_combo.config(values=headers)
            self.id_select_combo.current(0)
            self.name_select_combo.config(values=headers)
            self.name_select_combo.current(0)
        except:
            messagebox.showwarning("USGS Flow Loader","An unknown error occured while trying to load the file.")
    
    def open_help(self):
        """Attempt to open the help file PDF"""
        path = os.path.dirname(os.path.realpath(__file__))
        if getattr(sys, 'frozen', False):
            path = os.path.dirname(sys.executable)
        try:
            os.startfile(path+os.sep+"USGSFlowLoaderManual.pdf")
        except:
            messagebox.showwarning("USGS Flow Loader","Cannot find the USGS Flow Loader Manual. It should be located in the same directory as the application. If not, it may have been moved or deleted.")

    def set_work_dir(self):
        """Set a working directory."""
        work_dir = filedialog.askdirectory()
        if work_dir != "": #if they didn't press cancel
            self.work_dir = work_dir + os.sep
    
    def open_work_dir(self):
        """Open the working directory."""
        if self.work_dir != "":
            os.startfile(self.work_dir)
        else:
            messagebox.showwarning("USGS Flow Loader","You have not specified a working directory.")
        
    def return_column(self,column):
        """Return the values of a column from the input file as a list."""
        headers = self.in_file_data[0]
        column = headers.index(column)

        col_vals = []
        append = col_vals.append
        line_count = (1 if self.headers_check_var.get() == 1 else 0)
        for _ in range(len(self.in_file_data)):
            data = self.in_file_data[line_count]
            if (data[0] == '"' or data[0] == "'") and (data[-1] == "'" or data[-1] =='"'):
                data = [d[1:-1] for d in data]
            append(data[column])
            line_count += 1
            if line_count == len(self.in_file_data):
                break
        return col_vals

    def append_output_column(self,data,header):
        """Add a column of data to the output file."""
        v_vals = data[:]
        if self.output_data: #if there's already data
            v_vals.insert(0,header)
            line_count = 0
            output = []
            append = output.append
            for row in range(len(self.output_data)):
                data = self.output_data[row]
                d_append=data.append
                d_append(str(v_vals[row]))
                data = [str(val) for val in data]
                append(data)
                line_count += 1
                if line_count == len(self.output_data):
                    break
            self.output_data = output
        else:
            append = self.output_data.append
            v_vals.insert(0,header)
            for val in v_vals:
                append([str(val)])

    def write_data(self,file):
        """Attempt to write the output data to a file."""
        try:
            file = open(self.work_dir + file, 'w') 
            for i in range(len(self.output_data)):
                row = self.output_data[i]
                row = [str(val) for val in row]
                row = self.output_delimiter_str.get()[1:-1].join(row) + "\n"
                file.writelines(f"{row}") 
            file.close()
        except:
            self.text_box['state'] = 'normal'
            self.text_box.insert(tk.END, textwrap.dedent(f"An error occured while writing the data for station {file}").lstrip())
            self.text_box['state'] = 'disabled'
            self.text_box.see("end")

    def run(self):
        """Attempt to download flow data."""
        if not self.running:
            # first perform a check for incorrect parameters
            self.text_box['state'] = 'normal'
            self.text_box.delete('1.0', tk.END)
            self.text_box.insert(tk.END, textwrap.dedent("Checking input parameters...\n").lstrip())
            self.text_box['state'] = 'disabled'
            self.window.update_idletasks()
            can_run = True
            if self.station_notebook.select() == ".!labelframe.!notebook.!frame": #by file
                if not self.in_file_data:
                    can_run = False
                    messagebox.showwarning("USGS Flow Loader","Please choose a file to load station IDs and names.")
                else:
                    self.station_id = self.return_column(self.id_select_combo.get())
                    self.station_name = self.return_column(self.name_select_combo.get())
            elif self.station_notebook.select() == ".!labelframe.!notebook.!frame2": #manually
                if not self.manual_id_str.get() or not self.manual_name_str.get():
                    can_run = False
                    messagebox.showwarning("USGS Flow Loader","Please enter a list of station IDs and station names, separated by commas.")
                else:
                    try:
                        self.station_id = self.manual_id_str.get().strip().split(",")
                        self.station_name = self.manual_name_str.get().strip().split(",")
                    except:
                        can_run = False
                        messagebox.showwarning("USGS Flow Loader","Please check the format of station IDs and names.")
            if len(self.start_date.get()) < 10 or len(self.end_date.get()) < 10:
                can_run = False
                messagebox.showwarning("USGS Flow Loader","Please enter a start and end date in the correct format.")
            else:
                try:
                    parse(self.start_date.get())
                    parse(self.end_date.get())
                except:
                    can_run = False
                    messagebox.showwarning("USGS Flow Loader","Please use the correct format to specify dates.")
            if not self.output_delimiter_str.get().startswith('"') or not self.output_delimiter_str.get().endswith('"'):
                can_run = False
                messagebox.showwarning("USGS Flow Loader","Please enclose the output delimiter in double quotations.")
            if self.work_dir == "":
                can_run = False
                messagebox.showwarning("USGS Flow Loader","Please specify a working directory.")
            
            if not can_run:
                self.text_box['state'] = 'normal'
                self.text_box.delete('1.0', tk.END)
                self.text_box['state'] = 'disabled'

            # if all parameters appear correct, run the downloader
            if can_run:
                start = time.perf_counter()
                self.running = True
                self.text_box['state'] = 'normal'
                self.text_box.insert(tk.END, textwrap.dedent("Parameters OK, beginning download...\n").lstrip())
                self.text_box['state'] = 'disabled'
                num_stations = len(self.station_id)
                curr_percent = 0
                count = 0
                errors = 0
                for s in range(num_stations):
                    try:
                        # if we know the format of the url, we can substitute the station id and dates directly into the url to retreieve data
                        url = f"https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={'0'+self.station_id[s] if not self.station_id[s].startswith('0') else self.station_id[s]}&referred_module=sw&period=&begin_date={self.start_date.get()}&end_date={self.end_date.get()}"

                        page = urlopen(url) #returns an http response object

                        html_bytes = page.read() #returns page's html as a sequence of bytes
                        html = html_bytes.decode("utf-8") #parse those bytes into a string
                        extra = False # some data contains an extra variable, and must be accounted for
                        if "[Combined]" in html: #the extra variable is called "[Combined]"
                            extra = True

                        parsed = html.strip().split("\t") #convert the block of text into a list of strings.
                        parsed = parsed[14:] #actual data doesn't start until line 14

                        # retrieve dates and stream flow values
                        if not extra:
                            dates = [parsed[i] for i in range(0, len(parsed),4)] #retrieve the dates
                            vals = [parsed[i] for i in range(1, len(parsed),4)] #retrieve stream flow values
                        else: # for when there's an extra variable
                            dates = [parsed[i] for i in range(0, len(parsed),6)] #retrieve the dates
                            vals = [parsed[i] for i in range(1, len(parsed),6)] #retrieve stream flow values

                        # since US data is in cubic feet/s, we need to convert
                        out_vals = []
                        for v in vals:
                            try: #put it in a try block because some values are not numbers
                                if self.conversion_combo.get() == self.convert_vals[1]: #meters
                                    v = float(v) * 0.0283168 # m conversion factor
                                elif self.conversion_combo.get() == self.convert_vals[2]: #millimeters
                                    v = float(v) * 28316847 # mm conversion factor
                                elif self.conversion_combo.get() == self.convert_vals[0]: #no conversion
                                    v = float(v)
                                out_vals.append(v)
                            except: #if we can't parse it to float, its NaN, so just add it to the data as is
                                out_vals.append(v)

                        # add the date and value columns to a new file and write it
                        self.append_output_column(dates,"Date")
                        if self.conversion_combo.get() == self.convert_vals[1]: #meters
                            self.append_output_column(out_vals,f"Daily Discharge ({self.convert_vals[1]})")
                        elif self.conversion_combo.get() == self.convert_vals[2]: #millimeters
                            self.append_output_column(out_vals,f"Daily Discharge ({self.convert_vals[2]})")
                        elif self.conversion_combo.get() == self.convert_vals[0]:
                            self.append_output_column(out_vals,f"Daily Discharge ({self.convert_vals[0]})")
                        self.write_data(f"{self.station_name[s]} - {self.station_id[s]}{self.output_format_combo.get()}")
                        self.output_data.clear() #clear the output data to make room for the next file
                    except:
                        errors += 1
                        self.text_box['state'] = 'normal'
                        self.text_box.insert(tk.END, textwrap.dedent(f"Could not retreive data for {self.station_name[s]}, ID: {self.station_id[s]}\n").lstrip())
                        self.text_box['state'] = 'disabled'
                        self.text_box.see("end")

                    # update progress and window
                    count += 1
                    percent = int((count/num_stations) * 100)
                    if percent > curr_percent:
                        curr_percent = percent
                        self.progbar['value'] = curr_percent
                        self.progbar.update_idletasks()
                    self.window.update_idletasks()
                    
                # calculate time
                end = time.perf_counter()
                dur = end-start
                units = "seconds"
                if dur/3600 > 1:
                    dur /= 3600
                    units = "hours"
                elif dur/60 > 1:
                    dur /= 60
                    units = "minutes"

                self.running = False
                self.progbar['value'] = 0
                message = f"""
                Download complete!


                Time to completion: {dur:.2f} {units}
                Successful downloads: {num_stations-errors} of {num_stations} stations
                Failed downloads: {errors} station{'s' if errors != 1 else ''}"""
                messagebox.showinfo("USGS Flow Loader",textwrap.dedent(message).lstrip())


def main():
    app = FlowLoader()
    app.launch()

if __name__ == '__main__':
    main()