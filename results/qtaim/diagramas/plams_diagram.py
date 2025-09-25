#!/usr/bin/python3
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

with Diagram("Polarisability Workflow", direction="TB"):

    # adf = Custom("ADF", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/diagramas/ADF_logo.png")
    plams = Custom("plams", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/plams.png")
    
    with Cluster("SP"):
        adfdp = [Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png"),
                 Custom("ADF   ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png")]

    der = Custom("    ", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/plams.png")
    outf = Custom("output", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/SCMfile_icon.png")

    plams >> adfdp >> der >> outf

    # for adf_node in adf7:
    #     adf_node >> outf

