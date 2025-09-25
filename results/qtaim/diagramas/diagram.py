#!/usr/bin/python3
#!/opt/homebrew/bin/python3.9
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.aws.iot import IotGeneric

with Diagram("AMSuite", show=False):  # Force top-to-bottom layout
    # SCM input
    scm = Custom("AMS input", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/SCM_icon.png")
    # First Cluster - Engine with ADF, BAND, and DFTB
    with Cluster("Engine"):
        adf = Custom("ADF", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png")
        band = Custom("BAND", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/BAND_logo.png")
        dftb = Custom("DFTB", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/DFTB_logo.png")

    qtaim_local = Custom("QTAIM\nLocal Properties",
                         "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/SCM_icon.png")

    # Second Cluster - Non-local QTAIM and IQA
    with Cluster("ADF"):
        qtaim_non_local = Custom("QTAIM Non-Local\nProperties",
                                 "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png")
        iqa = Custom("IQA", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/ADF_logo.png")

    band2 = Custom("BAND", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/BAND_logo.png")
    dftb2 = Custom("DFTB", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/DFTB_logo.png")
    # Output node
    outf = Custom("output", "/Users/vcastor/Documents/PhD_Rouen/tesis/pdf/results/img/logos/SCMfile_icon.png")

    # Connections
    scm >> [dftb, band, adf]  # SCM input connects to ADF, BAND, DFTB
    [dftb, band, adf] >> qtaim_local  # ADF, BAND, DFTB connect to QTAIM Local Properties

    qtaim_local >> band2
    qtaim_local >> dftb2
    qtaim_local >> qtaim_non_local >> iqa >> outf  # Sequential connection from Local to Non-Local to IQA to output

    band2 >> outf
    dftb2 >> outf

