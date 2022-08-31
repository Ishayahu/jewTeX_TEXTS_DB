dirpath = r'D:\YandexDisk\Sites\jewTeX\TEXTS_DB\joseph_isaac_schneersohn\sefer_hamaamarim_5684\\'
t = """<?xml version="1.0" standalone="yes"?>
<content>
    <header level="1" type="dibur_amathil" number='{}' name="" jdate="">
        <page name="1">
            <header level="2" type="letter" number="1" name='alef'>
                <p></p>
            </header>
        </page>
    </header>
</content>"""
for x in range(1,31):
    with open(dirpath+f"{x:0>4}.xml",'w',encoding='utf8') as f:
        f.write(t.format(x))