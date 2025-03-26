import subprocess
from bs4 import BeautifulSoup
import csv
import os

# Here is the directory for the mg5_aMC program
# This directory must inlcude the typeIIIseesaw mechanism model in ./models file

mg5_relative_directory = "../../../mg5_spare/bin/mg5_aMC"


# This algorithm reads the cross section and uncertanity from the generated html tables.

def read_crossx(file_path):
    with open(file_path, "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        fourth_column_content = cells[3].text.strip()

    return fourth_column_content.split()

# built-in MadGraph5 CLI

def run_mg5_command(commands):

    # change stdout and stderr to subprocess.PIPE for preventing priniting in terminal (or set to None for priting)

    all_var = None

    process = subprocess.Popen(mg5_relative_directory,
        stdin=subprocess.PIPE,
        stdout=all_var,
        stderr=all_var,
        text=True)

    process.communicate(commands)

# ex.  output_file="data/simulation_data.csv"

def save_data(output_file,data,header):
    # Check if the file already exists
    file_exists = os.path.isfile(output_file)

    with open(output_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists and header:
            writer.writerow(header)
        writer.writerows(data)   

# Here the command lines and type of process we want to run in madgraph5

def cross_section_calculations_run():

    process = ["tr+ tr0", "tr+ tr-", "tr- tr0"]

    # mass_list=[100,120,140,160,180,200,220,240,250,260,280,300,320,340,360,380,400,450,500,550,600,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800]

    mass_list=[700]


    for i in process:
        for mass in mass_list:
            commands = f"""
            import model typeIIIseesaw
            generate p p > {i}
            output mg5_simulations/{"".join(i.split())}/{mass}GeV
            launch
            0
            ### RUN SETUP ###
            set nevents 100000
            set ebeam1 7000
            set ebeam2 7000
            ### Heavy leptons mass ###
            set Mtr0 {mass}
            set Mtrch {mass}
            set mtr {mass}
            set mtrm {mass}
            ## PDF ## here we use the NNPDF30_lo_as_0130 pdf set (following ATLAS Jopo)
            set pdlabel lhapdf
            set lhaid 263000  
            ### Mixings ###
            set ve 0
            set vm 0.063
            set vtt 0
            ### Acceptance cuts ###
            set ptj 20.0
            set ptl 10.0
            set etaj 5.0
            set etal 2.5
            set drjj 0.001
            set drll 0.0
            ### OTHER ###
            set sde_strategy 1  # Phase-Space Optimization strategy (integration strategy), 1 is for using using amp square
            set hard_survey 1  # i don't know what is that
            """
            try:
                run_mg5_command(commands)
                result = read_crossx(f'mg5_simulations/{"".join(i.split())}/{mass}GeV/crossx.html')
            except Exception as e:
                result = [0,0,0]

            save_data(f'data/{"".join(i.split())}.csv', [[mass,float(result[0])*1e3,float(result[2])*1e3]], ["mass","cross_pb", "unc_pb"])


def decay_width_calculations_run(ve,vm,vtt,case_no):

    # for case 1 we have: ve 0, vm 0.063, vtt 0

    decay_processes = ["tr+ > mu+ z", "tr+ > mu+ h", "tr+ > v w+", "tr0 > v z", "tr0 > v h", "tr0 > mu+ w-"]

    processes_names = [f'tr+_z_decay_case{case_no}', f'tr+_h_decay_case{case_no}', f'tr+_w_decay_case{case_no}',
                                         f'tr0_z_decay_case{case_no}', f'tr0_h_decay_case{case_no}', f'tr0_w_decay_case{case_no}']

    #mass_list=[100,110,120,130,140,150,160,180,200,220,240,250,260,280,300,320,340,360,380,400,450,500,550,600,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800]

    mass_list = [700]

    for process, name in zip(decay_processes, processes_names):
        for mass in mass_list:
            commands = f"""
            import model typeIIIseesaw
            define v = v1 v2 v3
            generate {process}  
            output mg5_simulations/decays/{name}/{mass}GeV
            launch
            0
            ### RUN SETUP ###
            set nevents 100000
            set ebeam1 7000
            set ebeam2 7000
            ### Heavy leptons mass ###
            set mtr0 {mass}
            set mtrch {mass}
            set mtr {mass}
            set mtrm {mass}
            ### Mixings ###
            set ve {ve} 
            set vm {vm}
            set vtt {vtt}
            ### Acceptance cuts ###
            set ptj 20.0
            set ptl 10.0
            set etaj 5.0
            set etal 2.5
            set drjj 0.001
            set drll 0.0
            ###Decay###
            #set wtr0 Auto
            #set wtrch Auto
            ### OTHER ###
            set sde_strategy 1
            set hard_survey 1
            """
            try:
                run_mg5_command(commands)
                result = read_crossx(f'mg5_simulations/decays/{name}/{mass}GeV/crossx.html')
            except Exception as e:
                result = [0,0,0]

            save_data(f'data/decays/{name}.csv', [[mass,float(result[0]),float(result[2])]],["mass","width", "unc_gev"])





#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
