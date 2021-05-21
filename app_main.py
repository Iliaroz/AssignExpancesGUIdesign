# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 13:15:25 2021

@author: kasia
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkcal
import time
import datetime as dt
import pandas as pd
from addTransaction import AddTransaction
from addCategory import AddCategory
from addContractor import AddContractor
import PeriodChooser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import app_import
from weather import Weather
import lotto
import matplotlib.dates as mdates
from PIL import ImageTk, Image

# fit matplotlib charts normally
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

## both format should match
_dt_datefmt = "%d.%m.%Y"
_cal_datefmt = "dd.mm.yyyy"

#######################################3


class FinanceApp:
    def __init__(self, master, dataBase):
        self.master = master
        # DataHandler instance
        ###self.badb = App_data()
        self.badb = dataBase
        
        # TODO: user manager handle
        
        # TODO: check user and call loginDialog ???
        
        # Main widget, build GUI
        self.mainwindow = self.__GUI(self.master)
        ### startup fun
        self.onStartup()
        ### BINDs
        # self.cal_tr_To.bind('<<DateEntrySelected>>', lambda x: self.updateTransactionTable() )
        # self.cal_tr_From.bind('<<DateEntrySelected>>', lambda x: self.updateTransactionTable() )
        self.tbl_transactions.bind("<Double-1>", self.h_tblTr_OnDoubleClick)
        self.tbl_categories.bind("<Double-1>", self.h_tblCat_OnDoubleClick)
        self.tbl_contractors.bind("<Double-1>", self.h_tblCont_OnDoubleClick)
        ## others
        self.ntb_app.bind("<<NotebookTabChanged>>", self.onTabChange)
        self.ntb_app.enable_traversal()
        self.tbl_contractors['show'] = 'headings'
        self.tbl_categories['show'] = 'headings'
        
        self.frm_tr_period.bind('<<PeriodSelected>>', self.updateTransactionTable )
        self.account_PeriodChooser.bind('<<PeriodSelected>>', self.chartOverallSpendings)
        self.cat_choosePeriod.bind('<<PeriodSelected>>', self.chartCategorySpendings)
        
        self.mainwindow.takefocus = True
        self.mainwindow.focus_set()
        
        if self.master == None:
            print("Finance application: run mainloop")
            self.mainwindow.mainloop()
        else:
            # self.mainwindow.grab_set()
            pass



    def initGraphs(self):
        ### CHARTS
        self.dpi = self.mainwindow.winfo_fpixels('1i')
        print(f"Current dpi is set to {self.dpi}")
        fig = plt.figure(dpi=self.dpi)
        self.ax1 = fig.add_subplot(111)
        self.ax1b = self.ax1.twinx()
        self.chart1 = FigureCanvasTkAgg(fig, self.lbfr_Acc_Chart)
        self.chart1.get_tk_widget().grid(padx='0',pady='0',
                column="0", row="0", sticky = 'nsew')
        self.lbfr_Acc_Chart.rowconfigure('0',weight='1')
        self.lbfr_Acc_Chart.columnconfigure('0',weight='1')
        fig = plt.figure(dpi=self.dpi)
        self.ax2 = fig.add_subplot(111)
        self.chart2 = FigureCanvasTkAgg(fig, self.lbfr_cat_Chart)
        self.chart2.get_tk_widget().grid(sticky='nsew', column="0",row="0")
        
           


    def onTabChange(self, event):
        tabIndex = str(self.ntb_app.index(self.ntb_app.select()))
        if tabIndex == "0":
            ## Account overview
            self.chartOverallSpendings(event)
            pass
        elif tabIndex == "1":
            ## Transaction tab
            self.updateTransactionTable()
            pass
        elif tabIndex == "2":
            ## Ctegories & contractors tab
            self.chartCategorySpendings(event)
            pass
        elif tabIndex == "3":
            ## Bells tab
            pass
        else:
            pass


    def getWeatherInfo(self):
        city = self.ent_ch_city.get()
        try:
            x = Weather(city)
            self.var_wt_location.set("Location : "+x.Location())
            self.var_wt_tempNum.set(x.Temperature())
            self.var_wt_type.set(x.Type())
            self.var_wt_windVal.set(x.WindSpeed())
            self.var_wt_pressureVal.set(x.Pressure())
            self.var_wt_tMinVal.set(x.TempMin())
            self.var_wt_tMaxVal.set(x.TempMax())
            self.var_wt_humidityVal.set(x.Humidity())
            
            img = tk.PhotoImage(data=x.Icon())
            self.lbl_wt_icon.configure(image=img)
            self.lbl_wt_icon.image= img
        except:
             tk.messagebox.showwarning("Wrong input city name!!",
                                      "This city name is incorrect.\n\nPlease, give correct city name.",
                                      parent=self.mainwindow)    
      

    def chartOverallSpendings(self, event):
        dates = self.account_PeriodChooser.get_datePeriod()
        start = dates[0]
        end = dates[1]
        
        self.display_balance(start, end)
        self.display_amountIn(start, end)
        self.display_amountOut(start, end)
        self.display_progressbar(start, end)
        
        income = self.badb.data_chartIncome(start,end)
        outcome = self.badb.data_chartOutcome(start,end)
        balance = self.badb.data_chartBalance(start,end)
        #print(i[0] for i in amount)
        am_income = [i[0] for i in income] 
        am_outcome = [(i[0]) for i in outcome ]
        am_balance = [i[0] for i in balance]
        
        # date_income = [(i[1].strftime(_dt_datefmt)) for i in income]
        # date_outcome = [(i[1].strftime(_dt_datefmt)) for i in outcome]
        # date_balance = [(i[1].strftime(_dt_datefmt)) for i in balance]
        
        date_income = [str(i[1]) for i in income]
        date_outcome = [str(i[1]) for i in outcome]
        date_balance = [str(i[1]) for i in balance]
        
        date_income = mdates.datestr2num(date_income)
        date_outcome = mdates.datestr2num(date_outcome)
        date_balance = mdates.datestr2num(date_balance)
    
        
        self.ax1.clear()
        self.ax1.plot(date_income, am_income, 
                      color='green', label='income', marker = '*')
        self.ax1.plot(date_outcome, am_outcome, 
                      color = 'red',label='outcome', marker = '.')
        self.ax1.axhline(y=0, color ='grey' )
        
        self.ax1b.clear()
        self.ax1b.bar(date_balance, am_balance, 
                       color = 'PaleGreen', label="balance", alpha = 0.4)
    
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter(_dt_datefmt))
        self.ax1b.xaxis.set_major_formatter(mdates.DateFormatter(_dt_datefmt))
        self.ax1.set_xlim(start,end)
        self.ax1b.set_xlim(start,end)
        
        start = start.strftime(_dt_datefmt)
        end = end.strftime(_dt_datefmt)
        
        self.ax1.set_title("Overall spendings for period: "+\
                  str(start)+" ---> "+str(end),
                  y=1.04, loc="center")
        # self.ax1.set_xlabel("Dates")
        self.ax1.set_ylabel("Balance [Euros]")
        self.ax1b.set_ylabel("Income/outcome [Euros]")
        self.ax1b.axhline(y=0, color ='PaleGreen' )
        self.ax1.legend( bbox_to_anchor=(0,1.08), 
                   loc="center")
        self.ax1b.legend( bbox_to_anchor=(1,1.05), 
                   loc="center")
        
        self.ax1b.grid(b=True, which='major', color='#999999', 
                       linestyle='--', linewidth = 0.8, alpha=0.2)
        self.ax1.grid(axis='x', linestyle='--', linewidth = 0.8)
        plt.gcf().autofmt_xdate()
        
        self.ax1.tick_params(axis='x', labelrotation=10)
        plt.tight_layout(pad=5, w_pad=5 , h_pad=5)
        self.chart1.draw()

        
    def chartCategorySpendings(self, event):
        dates = self.cat_choosePeriod.get_datePeriod()
        start = dates[0]
        end = dates[1]
        self.ax2.clear()
        amount = 0
        category = 1
        limit =2
       
        data = self.badb.data_chartCategories(start, end) 
        print(data)
        am = [abs(i[amount]) for i in data]
        cat=[i[category] for i in data]
        cat_limit = [i[limit] for i in data]
        
        try: 
            cat[cat.index(None)] = "Undefined"
            cat_limit[cat_limit(None)] = 0.0
        except: 
            print("no none categories")
            cat=[i[category] for i in data]
            
        start = start.strftime(_dt_datefmt)
        end = end.strftime(_dt_datefmt)
    
        self.ax2.bar(cat, cat_limit, align = 'edge', width =0.4 ,
                     color='PaleGreen', label = 'your limit')
        self.ax2.bar(cat,am, align = 'edge',width =  -0.4 ,
                     color = 'darkgreen', label = 'spendings')
        
        self.ax2.set_title("Spendings from: "+start+" to: "+ end)
        self.ax2.set_xlabel("Categories")
        self.ax2.set_ylabel("Spendings [Euros]")
        self.ax2.legend(loc=0)
        self.chart2.draw()

        
    def updateTransactionTable(self,event=None):
        #first clear the treeview
        for i in self.tbl_transactions.get_children():
            self.tbl_transactions.delete(i)
             
        #then display data
        
        dates = self.frm_tr_period.get_datePeriod()
        start = dates[0]
        end = dates[1]
        
        data = self.badb.getAllTransactionsPeriod(start, end)
        for row in data:
            idvalue = row[0]
            date = row[1].strftime(_dt_datefmt)
            cat = row[3] if row[3] else ""
            con = row[4] if row[4] else ""
            values = (idvalue, date, row[2], cat, con)
            self.tbl_transactions.insert('','end', values = values)
        # ***  
        #self.chartCategorySpendings()
        #self.chartOverallSpendings()


    def updateCategoriesTable(self):
        #first clear the treeview
        for item in  self.tbl_categories.get_children():
             self.tbl_categories.delete(item)
        #then display data
        data = self.badb.getCategoriesList()
        for row in data:
            cat = row[0] if row[0] else ""
            _id = row[1] if row[1] else ""
            values = (_id, cat)
            self.tbl_categories.insert('','end', values = values)
            
            
    def updateContractorsTable(self):
        #first clear the treeview
        for item in  self.tbl_contractors.get_children():
             self.tbl_contractors.delete(item)
        #then display data
        data = self.badb.getContractorList()
        for row in data:
            contr = row[0] if row[0] else ""
            _id = row[1] if row[1] else ""
            values = (_id, contr)
            self.tbl_contractors.insert('','end', values = values)      
            

    def h_btnTrAdd(self):
        addTransactionWindow = AddTransaction(self.mainwindow, self)
        #self.mainwindow.wait_window(addTransactionWindow)
        self.updateTransactionTable()


    def h_btnLogout(self):
        pass

    
    def h_tblTr_OnDoubleClick(self, event):
        ### Detect only item, on which was double clicked
        print("Double-clicked in table ", end='')
        clicked = self.tbl_transactions.identify('item',event.x,event.y)
        selected = self.tbl_transactions.selection()
        if len(selected) == 1:
            print("element.")
            id_value = str( self.tbl_transactions.item(clicked, 'values')[0] )
            print('Opening addTransaction window in "change" mode, id: ', id_value)
            AddTransaction(self.mainwindow, self, id_value)
            self.updateTransactionTable()
        else:
                print("somewhere. Not olnly one element selected or other area clicked.")

    
    def h_tblCat_OnDoubleClick(self, event):
        ### Detect only item, on which was double clicked
        print("Double-clicked in table ", end='')
        clicked = self.tbl_categories.identify('item',event.x,event.y)
        selected = self.tbl_categories.selection()
        if len(selected) == 1:
            print("element.")
            id_value = str( self.tbl_categories.item(clicked, 'values')[0] )
            print('Opening addCategory window in "change" mode, id: ', id_value)
            AddCategory(self.mainwindow, self, id_value)
            self.updateCategoriesTable()
        else:
            print("somewhere. Not olnly one element selected or other area clicked.")

    
    def h_tblCont_OnDoubleClick(self, event):
        ### Detect only item, on which was double clicked
        print("Double-clicked in table ", end='')
        clicked = self.tbl_contractors.identify('item',event.x,event.y)
        selected = self.tbl_contractors.selection()
        if len(selected) == 1:
            print("element.")
            id_value = str( self.tbl_contractors.item(clicked, 'values')[0] )
            print('Opening AddContractor window in "change" mode, id: ', id_value)
            AddContractor(self.mainwindow, self, id_value)
            self.updateContractorsTable()
        else:
                print("somewhere. Not olnly one element selected or other area clicked.")

        
    def h_btnTrChange(self):
        selected = self.tbl_transactions.selection()
        if len(selected) > 1:
            print("Multi selection in table. Cannot change several transactions yet.")
            tk.messagebox.showwarning("Change transaction",
                                   "Multi selection in table.\n\n Cannot change several transactions at once yet.",
                                      parent=self.mainwindow)
            return
        elif len(selected) == 1:
            print("One-line selection.")
            id_value = str(self.tbl_transactions.item(selected, 'values')[0])
            print('Opening addTransaction window in "change" mode, id: ', id_value)
            AddTransaction(self.mainwindow, self, id_value)
            self.updateTransactionTable()
        else:
            print("Nothing selected in table. Cannot change.")
            tk.messagebox.showwarning("Change transaction","Select transaction in table to change.",
                                      parent=self.mainwindow)


    def h_btnTrDelete(self):
        selected = self.tbl_transactions.selection()
        
        if len(selected) > 0:
            print("Some selection in table...")
            reply =  tk.messagebox.askyesno(title="Delete...", 
                           message=f"You going to delete {len(selected)} transactions.\n\n" + 
                                   "Are you sure?")
            if reply == True:
                for sel in selected:
                    id_value = self.tbl_transactions.item(sel, 'values')[0]
                    self.badb.deleteTransaction(id_value)
                self.updateTransactionTable()
            
        else:
            print("Nothing selected. Cannot delete.")
            tk.messagebox.showwarning("Delete transaction","Select transaction in table to delete.",
                                      parent=self.mainwindow)


    def h_btnTrImport(self):
        importWindow = app_import.ImportTransactionDialog(self.mainwindow, self)
        print("Import dialog is opened...")
        self.mainwindow.wait_window(importWindow.mainwindow)
        print("... Import dialog closed.")
        self.updateTransactionTable()
        pass


    def h_btnTrExport(self):
        exportingitems = self.tbl_transactions.get_children()
        ## Export choose: selected or all
        selected = self.tbl_transactions.selection()
        if len(selected) > 1:
            print("Multi selection in table. Choose dialog pop-up.")
            reply =  tk.messagebox.askyesno(title="Export...", 
                           message=f"There are {len(selected)} transactions selected in table." + 
                           "Choose what should be exported:\n\n" + 
                           "\tPress YES to export only selected.\n"
                           "\tPress NO to export whole table.")
            if reply == True:
                exportingitems = selected
        else:
            print("Nothing selected or only one line. Intend to export whole table.")
        
        filetypes = (
            ('CSV files', '*.csv'),
            #('Excel files', '*.xlsx'),
            ('All files', '*.*'))
        dates = self.frm_tr_period.get_datePeriod()
        start = dates[0]
        end = dates[1]
        exportFileName = "_".join(
                        ("Export",
                        start.strftime(_dt_datefmt),
                        end.strftime(_dt_datefmt) ))
        try:
            exportFileName = tk.filedialog.asksaveasfile(
                            title="Export current table view as...",
                            initialdir='./',
                            filetypes=filetypes,
                            defaultextension='.csv',
                            initialfile=exportFileName,
                            parent=self.mainwindow  )
        except PermissionError as err:
            print("Error: %s" %err)
            tk.messagebox.showerror("CSV export",
                        "Could not export: file writing error.\n\nPlease check file not used in other program.",
                        parent=self.mainwindow)
            return
        except:
            print("Some problem selecting file.")
            return
        # print("Selected filename for export: ", exportFileName.name )
        try:
            export_df = pd.DataFrame(None, columns=self.tbl_transactions_cols)
            for row in exportingitems:
                ## each row will come as a list under name "values" 
                rowvals = pd.DataFrame([self.tbl_transactions.item(row)['values']], 
                            columns=self.tbl_transactions_cols)
                export_df = export_df.append(rowvals)
            ## shrink dataframe to visible columns (no id of transaction)
            export_df = export_df[self.tbl_transactions_dcols]
        except:
            print("Unexpected error: cannot retrieve data from table.")
            tk.messagebox.showerror("CSV export",
                                    "Could not export: internal error",
                                    parent=self.mainwindow)
            return
        try:
            ## apply datetime format
            export_df.loc[:,'date'] = export_df.loc[:,'date'].apply(lambda x: dt.datetime.strptime(x, _dt_datefmt))
            export_df.to_csv(exportFileName, index = False)
        except:
            print("Unexpected error: cannot save data to csv.")
            tk.messagebox.showerror("CSV export",
                        "Could not export: file writing error.\n\nPlease check file not used in other program",
                        parent=self.mainwindow)
            return
        tk.messagebox.showinfo("CSV export",
                               "Export complete.",
                               parent=self.mainwindow)
        pass


    def h_btnTrLotto(self):
        date = dt.date.today()
        amount = lotto.check()
        self.badb.addTransaction(date, amount, "Lotto", None)
        if amount < 0:
            tk.messagebox.showwarning("LOTTO RESULTS!!!!","You have bad luck",
                                      parent=self.mainwindow)
        else:
            tk.messagebox.showwarning("LOTTO RESULTS!!!!","You won "+str(amount)+", yeay",
                                      parent=self.mainwindow)
        self.updateTransactionTable()


    def h_btnCatAdd(self):
        AddCategory(self.mainwindow, self)
        self.updateCategoriesTable()


    def h_btnCatChange(self):
        selected = self.tbl_categories.selection()
        print(selected)
        if len(selected) > 1:
            print("Multi selection in table. Cannot change several elements yet.")
            tk.messagebox.showwarning("Change category",
                                   "Multi selection in table.\n\n Cannot change several elements at once yet.",
                                      parent=self.mainwindow)
            return
        elif len(selected) == 1:
            print("One-line selection.")
            id_value = str(self.tbl_categories.item(selected, 'values')[0])
            print('Opening addCategory window in "change" mode, id: ', id_value)
            AddCategory(self.mainwindow, self, id_value)
            self.updateCategoriesTable()
        else:
            print("Nothing selected in table. Cannot change.")
            tk.messagebox.showwarning("Change category","Select category in table to change.",
                                      parent=self.mainwindow)


    def h_btnContractorsAdd(self):
        AddContractor(self.mainwindow, self)
        self.updateContractorsTable()

        
    def h_btnContractorsChange(self):
        selected = self.tbl_contractors.selection()
        print(selected)
        if len(selected) > 1:
            print("Multi selection in table. Cannot change several elements yet.")
            tk.messagebox.showwarning("Change contractor",
                                   "Multi selection in table.\n\n Cannot change several elements at once yet.",
                                      parent=self.mainwindow)
            return
        elif len(selected) == 1:
            print("One-line selection.")
            id_value = str(self.tbl_contractors.item(selected, 'values')[0])
            print('Opening addContractor window in "change" mode, id: ', id_value)
            AddContractor(self.mainwindow, self, id_value)
            self.updateContractorsTable()
        else:
            print("Nothing selected in table. Cannot change.")
            tk.messagebox.showwarning("Change contractor","Select contractor in table to change.",
                                      parent=self.mainwindow)

               
    def display_time(self):
        self.var_wt_CurrentTime.set( value= time.strftime('%H:%M:%S') )
        self.mainwindow.after(1000, self.display_time)     

    def display_progressbar(self, start, end):
        self.progressbar['value'] = 0
        outA = self.badb.getAmountOut(start, end)
        inA = val = self.badb.getAmountIn(start, end)
        if float(outA) == 0 or float(inA) == 0:
            percentage = 0
        else: percentage = float(abs(outA/inA))*100
        self.progressbar['value'] = percentage
        print(percentage)
        


    def display_balance(self, start, end):
        ## TODO: not by after
        val = self.badb.getBalance(start,end)
        self.var_CurrentBalance.set( value= f"{val:.2f}" )
        
        
    def display_amountIn(self, start, end):
        ## TODO: not by after
        val = self.badb.getAmountIn(start, end)
        self.var_perAmountIn.set( value= f"{val:.2f}" )
        
        
    def display_amountOut(self, start, end):
        val = self.badb.getAmountOut(start, end)
        self.var_perAmountOut.set( value= f"{val:.2f}" )
    

    def onStartup(self):
        #self.updateTransactionTable()
        self.updateCategoriesTable()
        self.updateContractorsTable()
        self.display_time()
        self.initGraphs()



    def __GUI(self, master):
        # build ui
        if master == None:
            self.root_app = tk.Tk()
        else:
            self.root_app = tk.Toplevel(master)

        ## Hide window 
        ## DO NOT forget to show at the end of init!!!
        self.root_app.withdraw()     
        
        ### Notebook 
        self.ntb_app = ttk.Notebook(self.root_app)
                        
        ###
        ### ACCOUNT TAB
        ###
        self.ntab_account = ttk.Frame(self.ntb_app)
        self.lbfr_account = ttk.Labelframe(self.ntab_account)
        self.progressbar = ttk.Progressbar(self.lbfr_account)
        self.progressbar.configure(orient='horizontal')
        self.progressbar.grid(column='3', padx='30', pady='10', row='0', sticky='ew')
        self.progressbar.master.columnconfigure('3', weight='1')
        self.lbfr_account.configure(height='200', text='Your account in summary', width='200')
        self.lbfr_account.grid(column='0', padx='10', pady='10', row='0', sticky='ew')
        self.lbfr_account.master.rowconfigure('0', pad='0', weight='0')
        self.lbfr_account.master.columnconfigure('0', weight='1')
        self.frm_acc_periodAbalance = ttk.Frame(self.ntab_account)
        self.lbfr_PeriodChooser = ttk.Labelframe(self.frm_acc_periodAbalance)
        self.account_PeriodChooser = PeriodChooser.PeriodChooserWidget(self.lbfr_PeriodChooser)
        self.account_PeriodChooser.grid(column='0', row='0', sticky='nsew')
        self.account_PeriodChooser.master.rowconfigure('0', weight='1')
        self.account_PeriodChooser.master.columnconfigure('0', weight='1')
        self.lbfr_PeriodChooser.configure(height='200', text='Period selector', width='200')
        self.lbfr_PeriodChooser.grid(column='0', padx='10', row='0', sticky='ns')
        self.lbfr_PeriodChooser.master.rowconfigure('0', pad='0')
        self.lbfr_PeriodChooser.master.columnconfigure('0', pad='0')
        self.lbfr_Balance = ttk.Labelframe(self.frm_acc_periodAbalance)
        self.lbl_balance = ttk.Label(self.lbfr_Balance)
        self.lbl_balance.configure(text='Balance')
        self.lbl_balance.grid(column='0', padx='10', row='0', sticky='e')
        self.lbl_balance2 = ttk.Label(self.lbfr_Balance)
        self.var_CurrentBalance = tk.StringVar(value='label10')
        self.lbl_balance2.configure(font='{Arial} 12 {bold}', text='label10', textvariable=self.var_CurrentBalance)
        self.lbl_balance2.grid(column='1', row='0', sticky='w')
        self.lbl_balance2.master.columnconfigure('1', weight='1')
        self.lbl_amountIn = ttk.Label(self.lbfr_Balance)
        self.lbl_amountIn.configure(text='Amount in:')
        self.lbl_amountIn.grid(column='0', padx='10', row='1', sticky='e')
        self.lbl_perAmountIn = ttk.Label(self.lbfr_Balance)
        self.var_perAmountIn = tk.StringVar(value='label4')
        self.lbl_perAmountIn.configure(font='{Arial} 12 {bold}', text='label4', textvariable=self.var_perAmountIn)
        self.lbl_perAmountIn.grid(column='1', row='1', sticky='w')
        self.lbl_perAmountIn.master.columnconfigure('1', weight='1')
        self.lbl_amountOut = ttk.Label(self.lbfr_Balance)
        self.lbl_amountOut.configure(text='Amount Out:')
        self.lbl_amountOut.grid(column='0', padx='10', row='3', sticky='e')
        self.lbl_perAmountOut = ttk.Label(self.lbfr_Balance)
        self.var_perAmountOut = tk.StringVar(value='label8')
        self.lbl_perAmountOut.configure(font='{Arial} 12 {bold}', text='label8', textvariable=self.var_perAmountOut)
        self.lbl_perAmountOut.grid(column='1', row='3', sticky='w')
        self.lbl_perAmountOut.master.columnconfigure('1', weight='1')
        self.lbfr_Balance.configure(height='200', text='Balance over period', width='200')
        self.lbfr_Balance.grid(column='1', row='0', sticky='nsew')
        self.lbfr_Balance.rowconfigure('0', weight='1')
        self.lbfr_Balance.rowconfigure('1', weight='1')
        self.lbfr_Balance.rowconfigure('2', weight='1')
        self.lbfr_Balance.master.rowconfigure('0', pad='0')
        self.lbfr_Balance.master.columnconfigure('1', pad='010', weight='1')
        # self.frm_acc_periodAbalance.configure(height='200', width='200')
        self.frm_acc_periodAbalance.grid(column='0', row='1', sticky='ew')
        self.frm_acc_periodAbalance.master.rowconfigure('1', weight='0')
        self.frm_acc_periodAbalance.master.columnconfigure('0', weight='1')
        self.lbfr_Acc_Chart = ttk.Labelframe(self.ntab_account)
        # self.lbfr_Acc_Chart.configure(height='200', width='200')
        self.lbfr_Acc_Chart.grid(column='0', padx='10', row='2', sticky='nsew')
        self.lbfr_Acc_Chart.master.rowconfigure('1', weight='1')
        self.lbfr_Acc_Chart.master.rowconfigure('2', weight='10000')
        self.lbfr_Acc_Chart.master.columnconfigure('0', weight='1')
        self.ntab_account.configure(height='200', padding='5', width='200')
        self.ntab_account.grid(column='0', row='0', sticky='nsew')
        self.ntab_account.master.rowconfigure('0', weight='1')
        self.ntab_account.master.columnconfigure('0', weight='1')
        self.ntb_app.add(self.ntab_account, sticky='nsew', text='Account', underline='0')

        ###
        ### TRANSACTIONS TAB
        ###
        self.frm_transactions = ttk.Frame(self.ntb_app)
        self.frm_tr_data = ttk.Frame(self.frm_transactions)
        self.frm_tr_data.grid(column = 0, row =0)
        
        self.lbfr_drTransactions = ttk.Labelframe(self.frm_transactions)
        self.frm_tr_period = PeriodChooser.PeriodChooserWidget(self.lbfr_drTransactions)
        self.frm_tr_period.grid(column = 0, row = 0, sticky = 'nsew')
        self.frm_tr_period.master.rowconfigure('0', weight=1)
        self.frm_tr_period.master.columnconfigure('0', weight=1)
        
        self.lbfr_drTransactions.configure(height='0', padding='0 0 20 0', text='Choose date range')  #
        self.lbfr_drTransactions.grid(column='0', ipadx='0', ipady='0', padx='5', pady='0', row='0', sticky='nsew')
        self.lbfr_drTransactions.master.rowconfigure('0', pad='10', weight=0)
        self.lbfr_drTransactions.master.columnconfigure('0', pad='0', weight=1)
        
        self.lbfr_Operations = ttk.Labelframe(self.frm_transactions)
        self.btn_trAdd = ttk.Button(self.lbfr_Operations)
        self.btn_trAdd.configure(text='Add', width='20')
        self.btn_trAdd.grid(column='0', row='0')
        self.btn_trAdd.master.rowconfigure('0', pad='10')
        self.btn_trAdd.master.columnconfigure('0', pad='10')
        self.btn_trAdd.configure(command=self.h_btnTrAdd)
        self.btn_trChange = ttk.Button(self.lbfr_Operations)
        self.btn_trChange.configure(text='Change', width='20')
        self.btn_trChange.grid(column='0', row='1')
        self.btn_trChange.master.rowconfigure('1', pad='10')
        self.btn_trChange.master.columnconfigure('0', pad='10')
        self.btn_trChange.configure(command=self.h_btnTrChange)
        self.btn_trDelete = ttk.Button(self.lbfr_Operations)
        self.btn_trDelete.configure(text='Delete', width='20')
        self.btn_trDelete.grid(column='0', row='2')
        self.btn_trDelete.master.rowconfigure('2', pad='10')
        self.btn_trDelete.master.columnconfigure('0', pad='10')
        self.btn_trDelete.configure(command=self.h_btnTrDelete)
        self.btn_trImport = ttk.Button(self.lbfr_Operations)
        self.btn_trImport.configure(text='Import CSV...', width='20')
        self.btn_trImport.grid(column='1', row='0')
        self.btn_trImport.master.rowconfigure('0', pad='10')
        self.btn_trImport.master.columnconfigure('1', pad='25')
        self.btn_trImport.configure(command=self.h_btnTrImport)
        self.btn_trExport = ttk.Button(self.lbfr_Operations)
        self.btn_trExport.configure(text='Export CSV...', width='20')
        self.btn_trExport.grid(column='1', row='1')
        self.btn_trExport.master.rowconfigure('1', pad='10')
        self.btn_trExport.master.columnconfigure('1', pad='25')
        self.btn_trExport.configure(command=self.h_btnTrExport)
        self.btn_trLotto = ttk.Button(self.lbfr_Operations)
        self.btn_trLotto.configure(cursor='no', text='Play lotto', width='15')
        self.btn_trLotto.grid(column='1', row='2')
        self.btn_trLotto.configure(command=self.h_btnTrLotto)
        self.lbfr_Operations.configure(height='0', text='Commands', width='200')
        self.lbfr_Operations.grid(column='1', padx='5', row='0', sticky='ns')
        self.lbfr_Operations.master.rowconfigure('0', pad='10', weight=0)
        
        self.lbfr_tableTransactions = ttk.Labelframe(self.frm_transactions)
        
        self.tbl_transactions = ttk.Treeview(self.lbfr_tableTransactions)
        self.scrb_trTableVert = ttk.Scrollbar(self.lbfr_tableTransactions)
        self.scrb_trTableVert.configure(orient='vertical')
        self.scrb_trTableVert.grid(column='1', row='0', sticky='ns')
        self.scrb_trTableVert.configure(command=self.tbl_transactions.yview)
        
        self.tbl_transactions_cols = [ 'id', 'date', 'amount', 'cat', 'cont' ]
        self.tbl_transactions_dcols = [      'date', 'amount', 'cat', 'cont' ]
        self.tbl_transactions.configure(columns=self.tbl_transactions_cols, 
                                        displaycolumns=self.tbl_transactions_dcols,
                                        yscrollcommand=self.scrb_trTableVert.set)
        self.tbl_transactions.column('id',      anchor='w',stretch='true',width='50',minwidth='20')
        self.tbl_transactions.column('date',    anchor='w',stretch='true',width='180',minwidth='20')
        self.tbl_transactions.column('amount',  anchor='w',stretch='true',width='180',minwidth='20')
        self.tbl_transactions.column('cat',     anchor='w',stretch='true',width='200',minwidth='20')
        self.tbl_transactions.column('cont',    anchor='w',stretch='true',width='200',minwidth='20')
        self.tbl_transactions.heading('id',       anchor='w',text='ID')
        self.tbl_transactions.heading('date',     anchor='w',text='Date')
        self.tbl_transactions.heading('amount',   anchor='w',text='Amount')
        self.tbl_transactions.heading('cat',      anchor='w',text='Category')
        self.tbl_transactions.heading('cont',     anchor='w',text='Contractor')
        self.tbl_transactions['show'] = 'headings'
        self.tbl_transactions.grid(column='0', padx='3', pady='3', row='0', sticky='nsew')
        self.tbl_transactions.master.rowconfigure('0', weight=1)
        self.tbl_transactions.master.columnconfigure('0', weight=1)
        
        self.lbfr_tableTransactions.grid(column='0', columnspan='2', padx='5', row='1', sticky='nsew')
        self.lbfr_tableTransactions.master.rowconfigure('1', weight=1)
        self.lbfr_tableTransactions.master.columnconfigure('0', pad='0', weight=1)
        self.frm_transactions.grid(column='0', padx='3', pady='10', row='0', sticky='nsew')
        self.frm_transactions.master.rowconfigure('0', weight=1)
        self.frm_transactions.master.columnconfigure('0', weight=1)
        self.ntb_app.add(self.frm_transactions, text='Trancations', underline='0')
        
        ###
        ### CATEGORIES TAB
        ###
        self.ntab_categories = ttk.Frame(self.ntb_app)
        self.frm_cat_Tables = ttk.Frame(self.ntab_categories)
        self.lbfr_tableCategories = ttk.Labelframe(self.frm_cat_Tables)
        self.lbfr_cat_Commands = ttk.Frame(self.lbfr_tableCategories)
        self.btn_catAdd = ttk.Button(self.lbfr_cat_Commands)
        self.btn_catAdd.configure(text='Add', width='10')
        self.btn_catAdd.grid(column='0', row='0')
        self.btn_catAdd.master.rowconfigure('0', pad='10')
        self.btn_catAdd.master.columnconfigure('0', pad='10')
        self.btn_catAdd.configure(command=self.h_btnCatAdd)
        self.btn_catChange = ttk.Button(self.lbfr_cat_Commands)
        self.btn_catChange.configure(text='Change', width='10')
        self.btn_catChange.grid(column='1', row='0')
        self.btn_catChange.master.rowconfigure('1', pad='10')
        self.btn_catChange.master.columnconfigure('0', pad='10')
        self.btn_catChange.configure(command=self.h_btnCatChange)
        self.lbfr_cat_Commands.configure(height='0', width='200')
        self.lbfr_cat_Commands.grid(sticky='new')
        self.lbfr_cat_Commands.master.rowconfigure('0', weight='0')
        self.lbfr_cat_Commands.master.columnconfigure('0', weight='1')
        self.frame3 = ttk.Frame(self.lbfr_tableCategories)
        self.tbl_categories = ttk.Treeview(self.frame3)
        self.scrb_catTableVert = ttk.Scrollbar(self.frame3)
        self.scrb_catTableVert.configure(orient='vertical', takefocus=False)
        self.scrb_catTableVert.grid(column='1', row='0', sticky='ns')
        self.scrb_catTableVert.master.columnconfigure('0', weight='1')
        self.scrb_catTableVert.configure(command=self.tbl_categories.yview)
        self.tbl_categories_cols = ['id', 'name']
        self.tbl_categories_dcols = ['name']
        self.tbl_categories.configure(columns=self.tbl_categories_cols, 
                                      displaycolumns=self.tbl_categories_dcols,
                                      yscrollcommand=self.scrb_catTableVert.set)
        self.tbl_categories.column('id', anchor='w',stretch='true',width='40',minwidth='20')
        self.tbl_categories.column('name', anchor='w',stretch='true',width='150',minwidth='50')
        self.tbl_categories.heading('id', anchor='center',text='ID')
        self.tbl_categories.heading('name', anchor='w',text='Category name')
        self.tbl_categories.grid(column='0', row='0', sticky='nsew')
        self.tbl_categories.master.rowconfigure('0', weight='1')
        self.tbl_categories.master.columnconfigure('0', weight='1')
        self.frame3.configure(height='200', width='200')
        self.frame3.grid(column='0', row='2', sticky='nsew')
        self.frame3.master.rowconfigure('2', weight='1')
        self.frame3.master.columnconfigure('0', weight='1')
        self.lbfr_tableCategories.configure(text='Categories')
        self.lbfr_tableCategories.grid(column='0', row='0', sticky='nsew')
        self.lbfr_tableCategories.master.rowconfigure('0', weight='1')
        self.lbfr_tableCategories.master.columnconfigure('0', weight='1')
        self.lbfr_tableContractors = ttk.Labelframe(self.frm_cat_Tables)
        self.lbfr_cont_Commands = ttk.Frame(self.lbfr_tableContractors)
        self.btn_contAdd = ttk.Button(self.lbfr_cont_Commands)
        self.btn_contAdd.configure(text='Add', width='10')
        self.btn_contAdd.grid(column='0', row='0')
        self.btn_contAdd.master.rowconfigure('0', pad='10')
        self.btn_contAdd.master.columnconfigure('0', pad='10')
        self.btn_contAdd.configure(command=self.h_btnContractorsAdd)
        self.btn_contChange = ttk.Button(self.lbfr_cont_Commands)
        self.btn_contChange.configure(text='Change', width='10')
        self.btn_contChange.grid(column='1', row='0')
        self.btn_contChange.master.rowconfigure('1', pad='10')
        self.btn_contChange.master.columnconfigure('0', pad='10')
        self.btn_contChange.configure(command=self.h_btnContractorsChange)
        self.lbfr_cont_Commands.configure(height='0', width='200')
        self.lbfr_cont_Commands.grid(sticky='new')
        self.lbfr_cont_Commands.master.rowconfigure('0', weight='0')
        self.lbfr_cont_Commands.master.columnconfigure('0', weight='1')
        self.frame1 = ttk.Frame(self.lbfr_tableContractors)
        self.tbl_contractors = ttk.Treeview(self.frame1)
        self.scrb_contTableVert = ttk.Scrollbar(self.frame1)
        self.scrb_contTableVert.configure(orient='vertical', takefocus=False)
        self.scrb_contTableVert.grid(column='1', row='0', sticky='ns')
        self.scrb_contTableVert.master.columnconfigure('0', weight='1')
        self.scrb_contTableVert.configure(command=self.tbl_contractors.yview)
        self.tbl_contractors_cols = ['id', 'name']
        self.tbl_contractors_dcols = ['name']
        self.tbl_contractors.configure(columns=self.tbl_contractors_cols, 
                                       displaycolumns=self.tbl_contractors_dcols,
                                       yscrollcommand=self.scrb_contTableVert.set)
        self.tbl_contractors.column('id', anchor='w',stretch='true',width='40',minwidth='20')
        self.tbl_contractors.column('name', anchor='w',stretch='true',width='150',minwidth='50')
        self.tbl_contractors.heading('id', anchor='center',text='ID')
        self.tbl_contractors.heading('name', anchor='w',text='Contractor name')
        self.tbl_contractors.grid(column='0', row='0', sticky='nsew')
        self.tbl_contractors.master.rowconfigure('0', weight='1')
        self.tbl_contractors.master.columnconfigure('0', weight='1')
        self.frame1.configure(height='200', width='200')
        self.frame1.grid(column='0', row='2', sticky='nsew')
        self.frame1.master.rowconfigure('2', weight='1')
        self.frame1.master.columnconfigure('0', weight='1')
        self.lbfr_tableContractors.configure(text='Contractors')
        self.lbfr_tableContractors.grid(column='0', row='1', sticky='nsew')
        self.lbfr_tableContractors.master.rowconfigure('0', weight='1')
        self.lbfr_tableContractors.master.rowconfigure('1', weight='1')
        self.lbfr_tableContractors.master.columnconfigure('0', weight='1')
        self.frm_cat_Tables.configure(height='100', padding='5 10 5 5', width='100')
        self.frm_cat_Tables.grid(column='0', row='0', sticky='nsew')
        self.frm_cat_Tables.master.rowconfigure('0', pad='0', weight='1')
        self.frm_cat_Tables.master.columnconfigure('0', minsize='200', pad='0', weight='1')
        self.frm_cat_Graphs = ttk.Frame(self.ntab_categories)
        
        self.lbfr_cat_data = ttk.Labelframe(self.frm_cat_Graphs)
        
        self.cat_choosePeriod = PeriodChooser.PeriodChooserWidget(self.lbfr_cat_data)
        self.cat_choosePeriod.grid(column='0', row='0', sticky='new')
        self.cat_choosePeriod.master.rowconfigure('0', weight='0')
        self.cat_choosePeriod.master.columnconfigure('0', weight='1')
        
        self.lbfr_cat_data.configure(height='100', text='Period selection')
        self.lbfr_cat_data.grid(column='0', row='0', sticky='new')
        self.lbfr_cat_data.master.rowconfigure('0', weight='0')
        self.lbfr_cat_data.master.columnconfigure('0', weight='1')
        
        self.lbfr_cat_Chart = ttk.Labelframe(self.frm_cat_Graphs)
        self.lbfr_cat_Chart.configure(height='200', text='Chart', width='200')
        self.lbfr_cat_Chart.grid(column='0', row='1', sticky='nsew')
        self.lbfr_cat_Chart.rowconfigure('0', weight ='1')
        self.lbfr_cat_Chart.columnconfigure('0', weight ='1')
        
        self.lbfr_cat_Chart.master.rowconfigure('1', weight='1')
        self.lbfr_cat_Chart.master.columnconfigure('0', weight='1')
        
        self.frm_cat_Graphs.configure(height='200', padding='5 10 5 5', width='200')
        self.frm_cat_Graphs.grid(column='1', row='0', sticky='nsew')
        self.frm_cat_Graphs.master.rowconfigure('0', pad='0', weight='1')
        self.frm_cat_Graphs.master.columnconfigure('1', weight='5')
        self.ntab_categories.configure(padding='0 5 0 0')
        self.ntab_categories.grid(column='0', row='0', sticky='nsew')
        self.ntab_categories.master.rowconfigure('0', weight='1')
        self.ntab_categories.master.columnconfigure('0', weight='1')
        self.ntb_app.add(self.ntab_categories, sticky='nsew', text='Categories & Contractors', underline='0')
        
        ###
        ### LOTTO TAB
        ###
        self.frm_bells = ttk.Frame(self.ntb_app)
        self.lbfr_bells_choose = ttk.Labelframe(self.frm_bells)
        
        self.lbl_ch_city = ttk.Label(self.lbfr_bells_choose)
        self.lbl_ch_city.configure(text='Please, write the city name in the box')
        self.lbl_ch_city.grid(column='0', padx='25', pady='10', row='0', sticky='e')
        self.lbl_ch_city.rowconfigure('0', pad='0', weight='0')
        self.lbl_ch_city.columnconfigure('0', pad='0')
        
        self.ent_ch_city = ttk.Entry(self.lbfr_bells_choose)
        self.ent_ch_city.grid(column='1', ipadx='20', row='0', sticky='ew')
        self.ent_ch_city.rowconfigure('0', pad='0', weight='0')
        self.ent_ch_city.columnconfigure('1', weight='1')
        
        self.btn_ch_city = ttk.Button(self.lbfr_bells_choose)
        self.btn_ch_city.configure(takefocus=False, text='Confirm', width='15')
        self.btn_ch_city.grid(column='2', row='0')
        self.btn_ch_city.rowconfigure('0', pad='0', weight='0')
        self.btn_ch_city.columnconfigure('2', pad='20', weight='0')
        self.btn_ch_city.configure(command=self.getWeatherInfo)
        
        self.lbfr_bells_choose.configure(height='200', padding='30 0', text='Choose city for which you want to have information displayed', width='200')
        self.lbfr_bells_choose.grid(column='0', padx='5', pady='0', row='0', sticky='nwe')
        self.lbfr_bells_choose.rowconfigure('0', pad='0', weight='1')
        self.lbfr_bells_choose.columnconfigure('0', pad='0', weight='1')
        self.lbfr_bells_choose.columnconfigure('1', pad='0', weight='1')
        self.lbfr_bells_choose.columnconfigure('2', pad='0', weight='1')
        
        self.lblfr_bells_weather = ttk.Labelframe(self.frm_bells)
        
        self.frm_wt_location = ttk.Frame(self.lblfr_bells_weather)
        self.lbl_wt_location = ttk.Label(self.frm_wt_location)
        self.var_wt_location = tk.StringVar(value='Please, enter the city name above')
        self.lbl_wt_location.configure(font='{Arial} 16 {}', text='Please, enter the city name above', textvariable=self.var_wt_location)
        self.lbl_wt_location.grid(column='0', pady='20', row='0', sticky='ew')
        self.lbl_wt_location.columnconfigure('0', weight='0')
        self.frm_wt_location.configure(height='200', width='200')
        self.frm_wt_location.grid(column='0', columnspan='2', row='0', sticky='n')
        self.frm_wt_location.columnconfigure('0', weight='1')
        
        self.frm_wt_values = ttk.Frame(self.lblfr_bells_weather)
        
        self.lbl_wt_type = ttk.Label(self.frm_wt_values)
        self.var_wt_type = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_type.configure(text='UNKNOWN', textvariable=self.var_wt_type)
        self.lbl_wt_type.grid(column='0', padx='20', pady='5', row='1')
        self.lbl_wt_type.columnconfigure('0', weight='0')
        
        self.lbl_wt_temperature = ttk.Label(self.frm_wt_values)
        self.lbl_wt_temperature.configure(text='Temperature')
        self.lbl_wt_temperature.grid(column='1', padx='10', pady='5', row='1', sticky='sew')
        
        self.lbl_wt_icon = ttk.Label(self.frm_wt_values)
        try:
            img = Image.open('pig1.ico')
            img = img.resize((50, 50), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            self.lbl_wt_icon.configure(image = img)
            self.lbl_wt_icon.image = img
        except: self.lbl_wt_icon.configure(text="????")
        self.lbl_wt_icon.grid(column='0', ipady = '10', padx='20', row='2', sticky='nsew')
              
        self.lbl_wt_tempNum = ttk.Label(self.frm_wt_values)
        
        self.var_wt_tempNum = tk.StringVar(value='???')
        # img = Image.open('temp.ico')
        # img = img.resize((50, 50), Image.ANTIALIAS)
        # img = ImageTk.PhotoImage(img)
        # self.lbl_wt_tempNum.configure(image = img)
        # self.lbl_wt_tempNum.image = img
        self.lbl_wt_tempNum.configure(font='{Arial} 16 {}', textvariable=self.var_wt_tempNum)
        self.lbl_wt_tempNum.grid(column='1', row='2')
        
        self.lbl_wt_wind = ttk.Label(self.frm_wt_values)
        self.lbl_wt_wind.configure(text='Wind')
        self.lbl_wt_wind.grid(column='0', padx='20', pady='5', row='3', sticky='se')
        self.lbl_wt_wind.rowconfigure('3', minsize='0', pad='40')
        self.lbl_wt_wind.columnconfigure('0', weight='0')
        
        self.lbl_wt_windVal = ttk.Label(self.frm_wt_values)
        self.var_wt_windVal = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_windVal.configure(text='UNKNOWN', textvariable=self.var_wt_windVal)
        self.lbl_wt_windVal.grid(column='1', padx='10', pady='5', row='3', sticky='sw')
        self.lbl_wt_windVal.rowconfigure('3', minsize='0', pad='40')
        
        self.lbl_wt_pressure = ttk.Label(self.frm_wt_values)
        self.lbl_wt_pressure.configure(text='Pressure')
        self.lbl_wt_pressure.grid(column='0', padx='20', pady='5', row='4', sticky='e')
        self.lbl_wt_pressure.columnconfigure('0', weight='0')
        
        self.lbl_wt_pressureVal = ttk.Label(self.frm_wt_values)        
        self.var_wt_pressureVal = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_pressureVal.configure(text='UNKNOWN', textvariable=self.var_wt_pressureVal)
        self.lbl_wt_pressureVal.grid(column='1', padx='10', pady='5', row='4', sticky='w')
        
        self.lbl_wt_tMax = ttk.Label(self.frm_wt_values)
        self.lbl_wt_tMax.configure(text='Temp.max')
        self.lbl_wt_tMax.grid(column='0', padx='20', pady='5', row='5', sticky='e')
        self.lbl_wt_tMax.rowconfigure('5', minsize='0')
        self.lbl_wt_tMax.columnconfigure('0', weight='0')
        self.lbl_wt_tMaxVal = ttk.Label(self.frm_wt_values)
        self.var_wt_tMaxVal = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_tMaxVal.configure(text='UNKNOWN', textvariable=self.var_wt_tMaxVal)
        self.lbl_wt_tMaxVal.grid(column='1', padx='10', pady='5', row='5', sticky='w')
        self.lbl_wt_tMaxVal.rowconfigure('5', minsize='0')
        
        self.lbl_wt_tMin = ttk.Label(self.frm_wt_values)
        self.lbl_wt_tMin.configure(text='Temp.min')
        self.lbl_wt_tMin.grid(column='0', padx='20', pady='5', row='6', sticky='e')
        self.lbl_wt_tMin.columnconfigure('0', weight='0')
        self.lbl_wt_tMinVal = ttk.Label(self.frm_wt_values)
        self.var_wt_tMinVal = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_tMinVal.configure(text='UNKNOWN', textvariable=self.var_wt_tMinVal)
        self.lbl_wt_tMinVal.grid(column='1', padx='10', pady='5', row='6', sticky='w')
        
        self.lbl_wt_humidity = ttk.Label(self.frm_wt_values)
        self.lbl_wt_humidity.configure(text='Humidity')
        self.lbl_wt_humidity.grid(column='0', padx='20', pady='5', row='7', sticky='e')
        self.lbl_wt_humidity.columnconfigure('0', weight='0')
        
        self.lbl_wt_humidityVal = ttk.Label(self.frm_wt_values)
        self.var_wt_humidityVal = tk.StringVar(value='UNKNOWN')
        self.lbl_wt_humidityVal.configure(text='UNKNOWN', textvariable=self.var_wt_humidityVal)
        self.lbl_wt_humidityVal.grid(column='1', padx='10', pady='5', row='7', sticky='w')
        
        self.frm_wt_values.configure(height='200', width='200')
        self.frm_wt_values.grid(column='0', row='1', sticky='nse')
        #self.frm_wt_values.columnconfigure('0', weight='1')
        
        self.frm_wt_calendar = ttk.Frame(self.lblfr_bells_weather)
        
        self.lbl_wt_today = ttk.Label(self.frm_wt_calendar)
        self.lbl_wt_today.configure(font='{Arial} 12 {}', text='Today is')
        self.lbl_wt_today.grid(column='0', padx='50', pady='10', row='0', sticky='nsw')
        self.lbl_wt_todayDate = ttk.Label(self.frm_wt_calendar)
        self.var_wt_todayDate = tk.StringVar(value='<todays date>')
        #self.var_wt_todayDate = tk.StringVar(value=dt.date.today().strftime(_dt_datefmt))
        self.var_wt_todayDate.set(dt.date.today().strftime(_dt_datefmt))
        self.lbl_wt_todayDate.configure(font='{Arial} 12 {}', text='<todays date>', textvariable=self.var_wt_todayDate)
        self.lbl_wt_todayDate.grid(column='1', row='0', sticky='nsw')
        
        self.lbl_wt_time = ttk.Label(self.frm_wt_calendar)
        self.lbl_wt_time.configure(font='{Arial} 12 {}', text='Time is')
        self.lbl_wt_time.grid(column='0', padx='50', pady='10', row='1', sticky='nsw')
        self.lbl_wt_timeNum = ttk.Label(self.frm_wt_calendar)
        self.var_wt_CurrentTime = tk.StringVar(value='<time>')
        self.lbl_wt_timeNum.configure(font='{Arial} 12 {}', text='<time>', textvariable=self.var_wt_CurrentTime)
        self.lbl_wt_timeNum.grid(column='1', row='1', sticky='nsw')
                
        self.var_Calendar = tk.StringVar(value='--.--.----')
        self.cal_wt = tkcal.Calendar(self.frm_wt_calendar, 
                                       selectmode='day', date_pattern=_cal_datefmt,
                                       textvariable=self.var_Calendar)
        self.cal_wt.grid(column='0', columnspan='2', padx='50', row='2', sticky='nsew')
        
        # self.cal_wt = CalendarFrame(self.frm_wt_calendar)
        # self.cal_wt.grid(column='0', columnspan='2', padx='50', row='2', sticky='s')
        self.cal_wt.rowconfigure('2', pad='30')
        
        self.lbl_wt_date = ttk.Label(self.frm_wt_calendar)
        self.lbl_wt_date.configure(font='{Arial} 12 {}', text='Selected date:')
        self.lbl_wt_date.grid(column='0', padx='50', pady='10', row='3', sticky='nsw')
        self.lbl_wt_date.rowconfigure('3', pad='10')
        
        self.lbl_wt_selection = ttk.Label(self.frm_wt_calendar)
        self.var_wt_selection = tk.StringVar(value='<Selected date>')
        self.lbl_wt_selection.configure(font='{Arial} 12 {}', text='<Selected date>', textvariable=self.var_Calendar)
        self.lbl_wt_selection.grid(column='1', row='3', sticky='nsw')
        self.lbl_wt_selection.rowconfigure('3', pad='10')
        
        self.frm_wt_calendar.configure(height='200', width='200')
        self.frm_wt_calendar.grid(column='1', row='1', sticky='nsw')
        self.frm_wt_calendar.columnconfigure('1', weight='1')
        
        self.lblfr_bells_weather.configure(height='200', padding='30 0', text='Weather', width='200')
        self.lblfr_bells_weather.grid(column='0', ipadx='10', padx='5', pady='5', row='1', 
                                      sticky='nwe')
        self.lblfr_bells_weather.rowconfigure('1', weight='0')
        self.lblfr_bells_weather.columnconfigure('0', pad='0', weight='1')
        self.lblfr_bells_weather.columnconfigure('1', pad='0', weight='1')
        
        self.frm_bells.configure(height='200', width='200')
        self.frm_bells.grid(column='0', row='0', sticky='nsew')
        # weight = 0, chose lblfr wont resize the row
        # self.frm_bells.rowconfigure('0', weight='1')
        self.frm_bells.rowconfigure('1', weight='1')
        self.frm_bells.columnconfigure('0', weight='1')
        
        self.frm_bells.rowconfigure('1', weight='1')        

        self.ntb_app.add(self.frm_bells, text='Weather and calendar', underline='0')
        
        ### NOTEBOOK GRID ...
        self.ntb_app.configure(style='Toolbutton', takefocus=True)
        self.ntb_app.grid(column='0', padx='5', pady='5', row='0', sticky='nsew')
        self.ntb_app.master.rowconfigure('0', weight=1)
        self.ntb_app.master.columnconfigure('0', weight=1)
        self.root_app.configure(relief='flat')
        self.root_app.geometry('1000x500')
        self.root_app.minsize(800, 400)
        self.root_app.resizable(True, True)
        self.root_app.title('Python cash')
        self.root_app.iconbitmap('pig1.ico')
        
        # SHOW window, fully constructed
        self.root_app.deiconify()
        ### 
        return self.root_app

