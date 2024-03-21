from pcap_handler import *

pcap2df = pcapHandler(file="dump.pcap", verbose=True)
df = pcap2df.to_DF(head=True)
df2csv = dfHandler(dataFrame=df, verbose=True)
df2csv.to_CSV(outputPath="dump.csv")