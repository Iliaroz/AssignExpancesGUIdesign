# -*- coding: utf-8 -*-
"""
Created on Thu May  6 19:00:12 2021

@author: ilia
"""

import tkinter as tk
import tkinter.ttk as ttk
import os.path
import pandas as pd
import tkinter.filedialog as fd
import datetime
import dateutil.parser 
import collections





class ImportApp:
    def __init__(self, master=None):
        # build ui
        self.root_import = tk.Tk() if master is None else tk.Toplevel(master)
        self.GUI(self.root_import)
        self.root_import.configure(height='300', relief='flat', width='300')
        self.root_import.geometry('700x400')
        self.root_import.minsize(600, 300)
        self.root_import.resizable(True, True)
        self.root_import.title('Import transactions from CSV...')

        # Main widget
        self.mainwindow = self.root_import
        
        ## BINDs
        self.mainwindow.bind_class("TCombobox","<<ComboboxSelected>>", self.updatePreview)
        self.mainwindow.bind('<Escape>', lambda x: self.mainwindow.destroy() )
        
        self.__df = pd.DataFrame()
        
    def detect_separator(self, filePath):
        """
        Detect separator in CSV
        Main idea, that in each line there is the same count of separators
        It will not work for quoted string

        """
        fileh = open(filePath, 'r')
        # read only first 4kB, hope few lines will be there
        Lines = fileh.readlines(4096)
        histograms = []
        result = []
        for i, line in enumerate(Lines):
            cnt = collections.Counter(line)
            histograms.append( cnt )
            if i == 0:
                intersection = cnt
            else:
                intersection = intersection & cnt
        del intersection['\n']
        for char in intersection:
            ok = 1
            num = histograms[0][char]
            for hist in histograms:
                if num != hist[char]:
                    ok = 0
            if ok == 1:
                result.append(char)
        return result
    
    def h_btnOpen(self):
        filetypes = (
            ('CSV files', '*.csv'),
            ('All files', '*.*'))

        filePath = fd.askopenfilename(
                title='Open a CSV file ...',
                initialdir='./',
                filetypes=filetypes)
        
        if not os.path.isfile(filePath):
            print("No file selected. (or not ordinary file selected)")
            ### GUI message
            # ...
            return
            
        sep = self.detect_separator(filePath)
        try:
            self.__df = pd.read_csv(filePath, sep=sep[0])
        except:
            print("Some error happend during opening csv file")
            # TODO: show some gui error message
            tk.messagebox.showwarning("CSV loading error",
                                  "Could not load csv file.\n\nPlease, select correct file.",
                                  parent=self.mainwindow)
            return
        try:
            cols = list(self.__df.columns)
            self.cmb_Date['values'] = cols
            self.cmb_Amount['values'] = cols
            self.cmb_Category['values'] = cols
            self.cmb_Contractor['values'] = cols
        except:
            print("Some error happend during parsing csv file")
            # TODO: show some gui error message
            tk.messagebox.showwarning("CSV loading error",
                                  "Could not parse csv file.\n\nPlease, select correct file.",
                                  parent=self.mainwindow)
            return


    def processTable(self, mode='preview'):
        self.progressbar['maximum'] = len(self.__df) // 100
        #first clear the treeview
        self.tbl_transactions.delete(*self.tbl_transactions.get_children())
        
        date_col = self.cmb_Date.get()
        amount_col = self.cmb_Amount.get()
        cat_col = self.cmb_Category.get()
        cont_col = self.cmb_Contractor.get()
        cols = list([ date_col, amount_col, cat_col, cont_col])
        ### Select data from all file
        subdf = pd.DataFrame()
        for i, col in enumerate(cols):
            if col :
                if mode == 'preview':
                    subdf.insert(len(subdf.columns), col, self.__df[col].head(20) , allow_duplicates=True)
                elif (mode == 'check') or (mode == 'import'):
                    subdf.insert(len(subdf.columns), col, self.__df[col] , allow_duplicates=True)
            else:
                subdf.insert(i, str(i) , ''  )
        
        ### Process data: 
            
        if (mode == 'check') or (mode == 'import'):
            if amount_col == '':
                tk.messagebox.showwarning("CSV column selection",
                                      "Column for amount_col is not selected.\n\nPlease, select column corresponding to amount.",
                                      parent=self.mainwindow)
                return
            ## TODO: convert types
            subdf.dropna(subset=list([amount_col,]), inplace=True)

        ### Process data
        self.progressbar.start()
        for index, row in subdf.iterrows():
            if index % 100 == 0:
                self.progressbar.update()
            tag = ""
            if mode == 'preview':
                self.tbl_transactions.insert('','end', values = ( [(index+1)] + list(row)) )
            elif (mode == 'check') or (mode == 'import'):
                ## Check values
                if row[amount_col] == 0.0:
                    subdf.at[index, date_col] = pd.NaN
                    tag += "DELETED"
                if self.set_dateToday:
                    resdate = datetime.datetime.now().date()
                    tag += ", DATE" 
                else:
                    try:
                        resdate = dateutil.parser.parse( row[date_col] )
                    except:
                        resdate = datetime.datetime.now().date()
                        tag += ", exDATE" 
                subdf.at[index, date_col] = str(resdate)
                result = str(index+1) + " " + tag
                iid = self.tbl_transactions.insert('','end', values = ( [result] + list(row))  )
        
        ### Do import after all checks
        if mode == 'import':
            subdf.dropna(subset=list([amount_col,]), inplace=True)
            # TODO: import into database
        self.progressbar.stop()
        pass


    def updatePreview(self, event):
        self.processTable()
        pass
    
    
    def h_btnCheck(self):
        self.processTable(mode='check')


    def h_btnImport(self):
        self.processTable(mode='import')
        pass

    def tbl_transactions(self, mode=None, value=None, units=None):
        pass

    def run(self):
        self.mainwindow.mainloop()

    def GUI(self, master):
        self.frm_main = ttk.Frame(self.root_import)
        self.lbfr_Operations = ttk.Labelframe(self.frm_main)
        self.btn_Open = ttk.Button(self.lbfr_Operations)
        self.btn_Open.configure(text='Open CSV...', width='20')
        self.btn_Open.grid(column='0', row='0')
        self.btn_Open.master.rowconfigure('0', pad='10')
        self.btn_Open.master.columnconfigure('0', pad='10')
        self.btn_Open.master.columnconfigure('1', pad='25')
        self.btn_Open.configure(command=self.h_btnOpen)
        self.btn_Check = ttk.Button(self.lbfr_Operations)
        self.btn_Check.configure(text='Check', width='20')
        self.btn_Check.grid(column='0', row='1')
        self.btn_Check.master.rowconfigure('1', pad='10')
        self.btn_Check.master.columnconfigure('0', pad='10')
        self.btn_Check.master.columnconfigure('1', pad='25')
        self.btn_Check.configure(command=self.h_btnCheck)
        self.btn_Import = ttk.Button(self.lbfr_Operations)
        self.btn_Import.configure(text='Import', width='20')
        self.btn_Import.grid(column='0', row='2')
        self.btn_Import.master.rowconfigure('0', pad='10')
        self.btn_Import.master.rowconfigure('2', pad='10')
        self.btn_Import.master.columnconfigure('0', pad='10')
        self.btn_Import.master.columnconfigure('1', pad='25')
        self.btn_Import.configure(command=self.h_btnImport)
        self.lbfr_Operations.configure(height='0', text='Commands', width='150')
        self.lbfr_Operations.grid(column='0', padx='5', row='0', sticky='ns')
        self.lbfr_Operations.master.rowconfigure('0', pad='0', weight='0')
        self.lbfr_Operations.master.columnconfigure('0', pad='0', weight='0')
        ## sub Frame selections
        self.lbfr_dataSelect = ttk.Labelframe(self.frm_main)
        self.lbl_corrDate = ttk.Label(self.lbfr_dataSelect)
        self.lbl_corrDate.configure(text='Date:')
        self.lbl_corrDate.grid(column='0', row='0', sticky='e')
        self.lbl_corrDate.master.rowconfigure('0', pad='5')
        self.lbl_corrDate.master.columnconfigure('0', pad='10')
        self.lbl_corrAmount = ttk.Label(self.lbfr_dataSelect)
        self.lbl_corrAmount.configure(text='Amount:')
        self.lbl_corrAmount.grid(column='0', row='1', sticky='e')
        self.lbl_corrAmount.master.rowconfigure('1', pad='5')
        self.lbl_corrAmount.master.columnconfigure('0', pad='10')
        self.lbl_Category = ttk.Label(self.lbfr_dataSelect)
        self.lbl_Category.configure(text='Category:')
        self.lbl_Category.grid(column='0', row='2', sticky='e')
        self.lbl_Category.master.rowconfigure('1', pad='10')
        self.lbl_Category.master.rowconfigure('2', pad='5')
        self.lbl_Category.master.columnconfigure('0', pad='10')
        self.lbl_Cont = ttk.Label(self.lbfr_dataSelect)
        self.lbl_Cont.configure(text='Contractor:')
        self.lbl_Cont.grid(column='0', row='3', sticky='e')
        self.lbl_Cont.master.rowconfigure('3', pad='5')
        self.lbl_Cont.master.columnconfigure('0', pad='10')
        self.cmb_Date = ttk.Combobox(self.lbfr_dataSelect)
        self.cmb_Date.configure(state='readonly')
        self.cmb_Date.grid(column='1', padx='10', row='0', sticky='ew')
        self.cmb_Date.master.rowconfigure('0', pad='5')
        self.cmb_Date.master.columnconfigure('1', pad='0', weight='1')
        self.cmb_Amount = ttk.Combobox(self.lbfr_dataSelect)
        self.cmb_Amount.configure(state='readonly')
        self.cmb_Amount.grid(column='1', padx='10', row='1', sticky='ew')
        self.cmb_Amount.master.rowconfigure('1', pad='5')
        self.cmb_Amount.master.columnconfigure('1', pad='0', weight='1')
        self.cmb_Category = ttk.Combobox(self.lbfr_dataSelect)
        self.cmb_Category.configure(state='readonly')
        self.cmb_Category.grid(column='1', padx='10', row='2', sticky='ew')
        self.cmb_Category.master.rowconfigure('1', pad='10')
        self.cmb_Category.master.rowconfigure('2', pad='5')
        self.cmb_Category.master.columnconfigure('1', pad='0', weight='1')
        self.cmb_Contractor = ttk.Combobox(self.lbfr_dataSelect)
        self.cmb_Contractor.configure(state='readonly')
        self.cmb_Contractor.grid(column='1', padx='10', row='3', sticky='ew')
        self.cmb_Contractor.master.rowconfigure('3', pad='5')
        self.cmb_Contractor.master.columnconfigure('1', pad='0', weight='1')
        self.chk_dateToday = ttk.Checkbutton(self.lbfr_dataSelect)
        self.set_dateToday = tk.IntVar(value=0)
        self.chk_dateToday.configure(text='Set date as today', variable=self.set_dateToday)
        self.chk_dateToday.grid(column='2', padx='10', row='0', sticky='w')
        self.chk_dateToday.master.rowconfigure('0', pad='5')
        self.chb_WithdrawalOnly = ttk.Checkbutton(self.lbfr_dataSelect)
        self.set_WithdrawalOnly = tk.IntVar(value=0)
        self.chb_WithdrawalOnly.configure(text='All as withdrawal', variable=self.set_WithdrawalOnly)
        self.chb_WithdrawalOnly.grid(column='2', padx='10', row='1', sticky='w')
        self.chb_WithdrawalOnly.master.rowconfigure('1', pad='5')
        self.chk_categoryAddNew = ttk.Checkbutton(self.lbfr_dataSelect)
        self.set_categoryAdd = tk.IntVar(value=0)
        self.chk_categoryAddNew.configure(text='Add new categories', variable=self.set_categoryAdd)
        self.chk_categoryAddNew.grid(column='2', padx='10', row='2', sticky='w')
        self.chk_categoryAddNew.master.rowconfigure('1', pad='10')
        self.chk_categoryAddNew.master.rowconfigure('2', pad='5')
        self.chk_contractorAddNew = ttk.Checkbutton(self.lbfr_dataSelect)
        self.set_contractorAdd = tk.IntVar(value=0)
        self.chk_contractorAddNew.configure(text='Add new contractors', variable=self.set_contractorAdd)
        self.chk_contractorAddNew.grid(column='2', padx='10', row='3', sticky='w')
        self.chk_contractorAddNew.master.rowconfigure('3', pad='5')
        self.lbfr_dataSelect.configure(height='0', padding='10 10', text='Select CSV columns correspond to... ', width='150')
        self.lbfr_dataSelect.grid(column='1', padx='5', row='0', sticky='nsew')
        self.lbfr_dataSelect.master.rowconfigure('0', pad='0', weight='0')
        self.lbfr_dataSelect.master.columnconfigure('0', pad='0', weight='1')
        self.lbfr_dataSelect.master.columnconfigure('1', weight='1')
        ## subFrame
        self.lbfr_tableTransactions = ttk.Labelframe(self.frm_main)
        self.tbl_transactions = ttk.Treeview(self.lbfr_tableTransactions)
        self.scrb_TableVert = ttk.Scrollbar(self.lbfr_tableTransactions)
        self.scrb_TableVert.configure(orient='vertical')
        self.scrb_TableVert.grid(column='1', row='0', sticky='ns')
        self.scrb_TableVert.configure(command=self.tbl_transactions.yview)
        self.tbl_transactions_cols = ['check','date', 'amount', 'cat', 'contr']
        self.tbl_transactions_dcols = ['check', 'date', 'amount', 'cat', 'contr']
        self.tbl_transactions.configure(columns=self.tbl_transactions_cols, 
                                        displaycolumns=self.tbl_transactions_dcols,
                                        yscrollcommand=self.scrb_TableVert.set)
        self.tbl_transactions.column('check', anchor='w',stretch='true',width='80',minwidth='20')
        self.tbl_transactions.column('date', anchor='w',stretch='true',width='80',minwidth='20')
        self.tbl_transactions.column('amount', anchor='w',stretch='true',width='50',minwidth='20')
        self.tbl_transactions.column('cat', anchor='w',stretch='true',width='150',minwidth='20')
        self.tbl_transactions.column('contr', anchor='w',stretch='true',width='150',minwidth='20')
        self.tbl_transactions.heading('date', anchor='w',text='Date')
        self.tbl_transactions.heading('amount', anchor='w',text='Amount')
        self.tbl_transactions.heading('cat', anchor='w',text='Category')
        self.tbl_transactions.heading('contr', anchor='w',text='Contractor')
        self.tbl_transactions['show']='headings'
        self.tbl_transactions.grid(column='0', padx='3', pady='3', row='0', sticky='nsew')
        self.tbl_transactions.master.rowconfigure('0', weight='1')
        self.tbl_transactions.master.columnconfigure('0', weight='1')
        self.lbfr_tableTransactions.grid(column='0', columnspan='2', padx='5', row='1', sticky='nsew')
        self.lbfr_tableTransactions.master.rowconfigure('1', weight='1')
        self.lbfr_tableTransactions.master.columnconfigure('0', pad='0', weight='0')
        self.progressbar = ttk.Progressbar(self.lbfr_tableTransactions)
        self.progressbar.configure(orient='horizontal', 
                                   mode='determinate',
                                   takefocus=False )
        self.progressbar.grid(column='0', row='1', padx='5', pady='1', sticky='ew')
        self.frm_main.configure(height='400', width='400')
        self.frm_main.grid(column='0', padx='3', pady='10', row='0', sticky='nsew')
        self.frm_main.master.rowconfigure('0', weight='1')
        self.frm_main.master.columnconfigure('0', weight='1')
        ### ====================================================
        ### END GUI        

if __name__ == '__main__':
    app = ImportApp()
    app.run()

