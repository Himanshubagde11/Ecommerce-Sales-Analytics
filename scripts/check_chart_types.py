import os

bin_dir = r"C:\Program Files\Microsoft Power BI Desktop\bin"

for f in ["Microsoft.PowerBI.Client.Windows.dll", "Microsoft.PowerBI.Packaging.dll", "Microsoft.PowerBI.Modeler.dll"]:
    fp = os.path.join(bin_dir, f)
    if os.path.exists(fp):
        with open(fp, "rb") as fo:
            data = fo.read()
            for candidate in [
                b"lineClusteredColumnComboChart",
                b"lineStackedColumnComboChart",
                b"clusteredColumnComboLineChart",
                b"comboChart",
                b"columnChart",
                b"barChart"
            ]:
                if candidate in data:
                    print(f"Found {candidate.decode()} in {f}!")
