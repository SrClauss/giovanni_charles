import pdfplumber
from PyPDF2 import PdfWriter, PdfReader
from tkinter import Tk, Button, Entry,  Label,  Frame, filedialog, StringVar

def cut_pdf(file_path, initial_page, final_page):
	reader = PdfReader(file_path)	
	writer = PdfWriter()

	num_pages = len(reader.pages)
	start = max(0, int(initial_page) - 1)
	end = min(num_pages, int(final_page))



	for i in range(start, end):

		page = reader.pages[i]
		writer.add_page(page)
	
	

	output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

	with open(output_path, 'wb') as output_pdf:
		writer.write(output_pdf)




if __name__ == "__main__":
	root = Tk()
	root.title("Cut PDF")
	root.geometry("300x300")

	frame = Frame(root)
	frame.pack(pady=20)

	path = StringVar()
	initial = StringVar()
	final = StringVar()

	Label(frame, text="Caminho do arquivo:").grid(row=0, column=0)
	file_path_entry = Entry(frame, width=30, state='readonly', textvariable=path)
	file_path_entry.grid(row=0, column=1)


	Label(frame, text="Página inicial:").grid(row=1, column=0)
	initial_page_entry = Entry(frame, width=30, textvariable=initial)
	initial_page_entry.grid(row=1, column=1)

	Label(frame, text="Página final:").grid(row=2, column=0)
	final_page_entry = Entry(frame, width=30, textvariable=final)
	final_page_entry.grid(row=2, column=1)

	button_selecionar_arquivo = Button(frame, text="Selecionar arquivo", command=lambda: path.set(filedialog.askopenfilename()))
	button_selecionar_arquivo.grid(row=3, column=0, columnspan=2)



	button_cut_pdf = Button(frame, text="Cortar PDF", command=lambda: cut_pdf(path.get(), initial.get(), final.get()))
	button_cut_pdf.grid(row=4, column=0, columnspan=2)



	



	root.mainloop()




