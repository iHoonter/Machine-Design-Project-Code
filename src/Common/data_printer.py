class DataPrinter:
    '''
    Class to specify uniform formatting of data throughout program.

    Parameters
    ----------
    format_spec : str

        A string specifying the format to be applied across all printed data. Ex: ".3f" or ".2e"

    importance_cutoff : int

        A number specifying the importance above which data will be printed. The show() function has a built-in importance level, if this 
        level is below the importance cutoff specified here the data won't be printed. A lower value is a higher importance, so if an 
        importance cutoff of 1 is provided then only show() statements with an importance level of 0 or 1 will be printed. 

    **print_args : dict

        All other kwargs are passed to the python print() function.
    '''
    def __init__(self, format_spec : str, importance_cutoff : int = 0, output_file : str | None = None) -> None:
        self.format_spec = format_spec
        self.importance_cutoff = importance_cutoff

        if output_file != None:
            self.print_to_file = True
            self.file = open(output_file, mode='w')
        else:
            self.print_to_file = False

    def __del__(self):
        if self.print_to_file:
            self.file.close()

    def show(self, data, importance_level : int = 0, label : str = '', section : str = None):
        '''
        Method to print data using format specified by printer object

        Parameters
        ----------
        data 

            The data to be printed

        importance_level : int = 0

            The importance of the statement to be printed. If importance is lower than cutoff then the statement won't be printed.

        label : str (optional)

            A label to be printed before the data. Ex. if label='Hello ', printed statment will look like "Hello {data}"

        title : str (optional)

            Prints a title string with seperation before and after, for visual seperation of data.
        '''
        if section != None:
            self.title(section, importance_level)
        if importance_level <= self.importance_cutoff:
            self._print(label + format(data, self.format_spec))

    def section(self, section_name : str, importance_level : int = 0):
        if importance_level <= self.importance_cutoff:
            self._print(f'\n{section_name}')

    def _print(self, string: str):
        if self.print_to_file:
            self.file.write(string + '\n')
        else:
            print(string)

