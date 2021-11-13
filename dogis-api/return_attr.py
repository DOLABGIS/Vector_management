# -*- coding: UTF-8 -*

# from tkinter import _TextIndex
from os import chdir
import psycopg2
from flask import Flask, jsonify, abort, make_response, request
import json
import numpy as np
import TIN
import shapely

app = Flask(__name__)

# connect to test db
conn = psycopg2.connect(database="test", user="postgres",
                        password="dogis2021", host="49.232.75.144", port="5432")

print("Opened database successfully")
cur = conn.cursor()

# query attr table
# http://49.232.75.144:9423/dogis/api/v1.0/attr_table
@app.route('/dogis/api/v1.0/attr_table', methods=['POST'])
def attr_table():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['file_name']='wuhan'
    file_name = jInfo['file_name']
    query = "SELECT * from "+file_name+';'
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
        return '0'
    rows = cur.fetchall()
    fields = cur.description
    conn.commit()

    rowList=[]
    for i in range(len(rows)):    
        rowList.append(list(rows[i][0:-1]))  # remove geom column
    fields = fields[:-1]  # remove geom field
    column_list = []
    for i in fields:
        column_list.append({'text':i[0],'value':i[0]})  # decompose tuple
    row_list = []
    for row in rows:
        tmp_result = {}
        for i in range(len(column_list)):
            tmp_result[column_list[i]['text']] = row[i]
        row_list.append(tmp_result)

    # 输出格式一
    json_dic = {}
    json_dic['title'] = column_list
    json_dic['content'] = row_list
    jsondata=json.dumps(json_dic, ensure_ascii=False)

    # print("Write to file successfully")
    return jsondata

# list 转成Json格式数据
def listToJson(name_list,lst):
    # keys = [str(x) for x in np.arange(len(lst))]
    keys = name_list
    list_json = dict(zip(keys, lst))
    str_json = json.dumps(list_json, indent=2, ensure_ascii=False)  # json转为string
    return str_json

# initial all table
# http://49.232.75.144:9423/dogis/api/v1.0/initial
@app.route('/dogis/api/v1.0/initial', methods=['GET'])
def initial():
    geojson_list = []
    query1="SELECT	table_name \
            FROM	information_schema. TABLES \
            WHERE	table_schema = 'public';"
    cur.execute(query1)
    names = cur.fetchall()
    conn.commit()

    name_list = [x[0] for x in names]
    
    name_list.remove('spatial_ref_sys')
    name_list.remove('geometry_columns')
    name_list.remove('geography_columns')
    name_list.remove('platform_user')
    for table_name in name_list:
        query_field = "SELECT * from "+table_name+';'
        cur.execute(query_field)
        cur_fields = cur.description
        field_str=""
        for field in cur_fields[0:-1]:
            field_str=field_str+field.name+","
        field_str=field_str[:-1]
        query_tmp = "SELECT \
                    row_to_json(fc) \
                    FROM ( \
                        SELECT \
                            'FeatureCollection' AS type \
                            , array_to_json(array_agg(f)) AS features \
                        FROM ( \
                            SELECT \
                                'Feature' AS type \
                                , ST_AsGeoJSON(geom)::json as geometry \
                                , ( \
                                    SELECT \
                                        row_to_json(t) \
                                    FROM ( \
                                        SELECT "+field_str+"\
                                        ) AS t \
                                    ) AS properties \
                            FROM "+table_name+"  \
                        ) AS f \
                    ) AS fc" 
        cur.execute(query_tmp)
        cur_geojson = cur.fetchall()
        conn.commit()
        geojson_list.extend(cur_geojson[0])
    return listToJson(name_list,geojson_list)

# drop table
# http://49.232.75.144:9423/dogis/api/v1.0/drop
@app.route('/dogis/api/v1.0/drop', methods=['POST'])
def drop():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['layer']='line1'
    table_name = jInfo['layer']
    query1 = "DROP TABLE "+table_name+";"
    try:
        cur.execute(query1)
        conn.commit()
    except Exception as e:
        return '0'
    return '1'


# update attr values
# http://49.232.75.144:9423/dogis/api/v1.0/update
@app.route('/dogis/api/v1.0/update', methods=['POST'])
def update():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['name']='wuhan'
    # jInfo['content'] = {'gid':'1','name':'长江新城','value':'0.999'}
    file_name = jInfo['layer']
    values = jInfo['content']
    v_str=""
    for i,k in enumerate(values):
        if i == 0:
            gid = values[k]
            continue
        v_str = v_str+k+" = '"+values[k]+"',"

    query1 = "UPDATE "+file_name+" SET "+v_str[:-1]+" WHERE gid = '" + str(gid) +"';"
    cur.execute(query1)
    conn.commit()

    query2 = "SELECT * from "+file_name+';'
    cur.execute(query2)
    rows = cur.fetchall()
    fields = cur.description
    conn.commit()

    rowList=[]
    for i in range(len(rows)):    
        rowList.append(list(rows[i][0:-1]))  # remove geom column
    fields = fields[:-1]  # remove geom field
    column_list = []
    for i in fields:
        column_list.append({'text':i[0],'value':i[0]})  # decompose tuple
    row_list = []
    for row in rows:
        tmp_result = {}
        for i in range(len(column_list)):
            tmp_result[column_list[i]['text']] = row[i]
        row_list.append(tmp_result)

    # 输出格式一
    json_dic = {}
    json_dic['title'] = column_list
    json_dic['content'] = row_list
    jsondata=json.dumps(json_dic, ensure_ascii=False)

    # print("Write to file successfully")
    return jsondata

# DELETE values
# http://49.232.75.144:9423/dogis/api/v1.0/delete
@app.route('/dogis/api/v1.0/delete', methods=['POST'])
def delete():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['layer']='wuhan'
    # jInfo['content'] = {'gid':'1','name':'长江新城','value':'0.999'}
    table_name = jInfo['layer']
    value = jInfo['gid']
    # for i,k in enumerate(values):
    #     if i == 0:
    #         key_field = k
    #         key_value = values[k]
    query1 = "DELETE FROM "+table_name+" WHERE gid = '" +str(value)+"';"
    cur.execute(query1)
    conn.commit()


    query_field = "SELECT * from "+table_name+';'
    cur.execute(query_field)
    cur_fields = cur.description
    field_str=""
    for field in cur_fields[0:-1]:
        field_str=field_str+field.name+","
    field_str=field_str[:-1]
    query_tmp = "SELECT \
                row_to_json(fc) \
                FROM ( \
                    SELECT \
                        'FeatureCollection' AS type \
                        , array_to_json(array_agg(f)) AS features \
                    FROM ( \
                        SELECT \
                            'Feature' AS type \
                            , ST_AsGeoJSON(geom)::json as geometry \
                            , ( \
                                SELECT \
                                    row_to_json(t) \
                                FROM ( \
                                    SELECT "+field_str+"\
                                    ) AS t \
                                ) AS properties \
                        FROM "+table_name+"  \
                    ) AS f \
                ) AS fc" 
    cur.execute(query_tmp)
    cur_geojson = cur.fetchall()
    conn.commit()
    return listToJson([table_name],cur_geojson)


# INSERT values
# http://49.232.75.144:9423/dogis/api/v1.0/insert
@app.route('/dogis/api/v1.0/insert', methods=['GET'])
def insert():
    # jInfo = request.get_json()
    jInfo={}
    jInfo['layer']='wuhan'
    jInfo['content'] = {'gid':'1','name':'new长江新城','value':'1.999','geom':'0106000020E710000001000000010300000001000000F3010000F6997FAB1AA35C402C3EE2F9AC893E40191964FD6DA35C40977137861C893E407B9D1338B5A35C4004BA9301A8883E402D6A5D2DF3A35C40779C6E5ABA883E40CF20BDE07DA45C40102E8FB5C7883E40F097F49BD2A45C40D9F1314978883E40DA0F07EE25A55C403E1CFAB4F5873E4097DD553037A55C40C3A0CAB02D873E4000B6AE213CA55C4075ACA6FDC2853E4057DD4F242DA55C40350778452E853E400C9428A10CA55C401752810987843E40C45AA76600A55C4001DF67192A843E40584C948AF9A45C407D92652FBF833E40B90A26C1D3A45C40DD479B5070833E40383B3567B3A45C4071FC8B434B833E4071063788B4A45C4030D4D9EA95823E40D3752E8D82A45C40092DA45801823E40CE41DB5F5BA45C405AB1299F88813E40825580883DA45C40BF04A974C5803E407CE9680025A45C40C063612AC17F3E4046E3898910A45C40A818341BD47E3E403E10828B24A45C407B9621933A7E3E40E600383B4EA45C406E1E367F1E7E3E4010CD77F377A45C40DAF9AF501E7E3E40FDB1725EA0A45C402210E055437E3E4083842A01CAA45C407ACA6665FD7D3E40C6DD20A4E3A45C40B5A5F513357E3E4022BAF3ECFFA45C402EE8D78B477E3E40CA41233E0DA55C4053F84F3CD37D3E40E43EB8AE49A55C406805CC4B717D3E40CE88AF995DA55C4074906BA6967C3E40B03F76AB52A55C406F757FDA0F7C3E40414E64C834A55C40A361A27E277B3E40A901062E27A55C40E21852A8AE7A3E4039188F5B01A55C40097A02EF357A3E407E88130AE5A45C4072D061EA027A3E402193F6AEF3A45C40CC94E7A480793E40A917E959C4A45C403CA649E8B8783E409619FEC1B6A45C40F821B9B644783E40FAD9BC6BC9A45C40CC337779B4773E40284CAA2EECA45C40AF962BF5FE763E4056B9A7F90EA55C401BCE0F5665763E40864124EF39A55C40570A55BA1A763E4014E9D83568A55C400EFCDEADDC753E403CF9EA4C30A55C40A42FACDDBC743E40457D87645CA55C40C0D009919C733E408F9B298E56A55C40E8A62E20B6723E40FC3CC4DE13A55C407DA5663DA3723E4008A2796FE1A45C402393198F36713E40E1A1F60AE1A45C4005F0150EF06F3E4060B8139D12A55C40BDD0BD1B966E3E401628F81E18A55C40B128D6AA6F6E3E40AD7441C633A55C40DD881B810F6E3E40CC82951C60A55C40B43E4676C26D3E403D6B3A6570A55C40DC7B18138F6C3E40CA12039259A55C408EA56FCE9B6A3E40B2F9A8D142A55C4092779326E2683E4059ABE4157AA55C40FDD313990E683E4095B1295E68A55C40A2755057AE643E408743345D51A55C40605F416021623E40C51B878A2EA55C401D58C5FB405D3E4049A76CCE70A55C40AD4B01BC335C3E404AF55316A7A55C40787126C95F583E40301BCB3C79A55C400BBF75FEB8533E40E657C1785AA55C40BBD8C7EB0A4A3E401F0C644A28A55C406996959F24493E404EFF54D517A45C40F85EF76C85463E40CC7017B7BEA35C4093797EC218453E4029B109949CA35C40D046596318423E405EC16FF46FA35C403D37D5CB1E413E4011B71CF1A1A25C40671CA8F3BE3D3E40864B00C327A25C4095783A94C53C3E407C14599626A25C40A308B8637E383E4075FB224263A25C40B28BE76784373E4036C58A7447A25C40C1C3356D24373E40499ECE081BA25C401807E17EC4363E408EDB07C2EEA15C409D1CC60FEB363E4038FD8BD6C7A15C40FCF16FAD64363E40DF1A4740E3A15C406AE6A19757353E406FFD6811C7A15C40174385858A333E407350D6A936A15C4062C4C6A00A323E40EA035E0CDEA05C40EE3580DB0A323E40AEA86F0796A05C4031FF23D1F7313E40CE31FF827FA05C408DAD04C78A303E4060E93B9C84A05C40401109CFD02E3E40AEFF081BA0A05C402FF99496102E3E402AB85A6684A05C40929E0570FD2D3E40F997510658A05C40E7A11DADB02D3E4004DEAF892BA05C4067C6C79CF02C3E40BE04D05978A05C40057F3A72292A3E4049B201433BA05C405D5A406B69293E406BD9AC9F9F9F5C40154AA45DDC263E402D3BB9C6D69F5C407E88E2DF08263E40840A9D27F29F5C4054C93559D5243E409C6EDECADB9F5C40659FCEC9EE233E40F87205BAC59F5C40BF02D3B23B243E408C041F5B999F5C40BD616EB2DB233E402682928F9E9F5C40847013C681223E40B01262ACA39F5C4071CEA8C2C7203E40E4724DDA53A05C402BC332F12C1D3E40C579598690A05C404D654B9F6C1C3E40C173767D69A05C408EB0AA37391B3E405A59917E8AA05C404F72FFF4781A3E40A4D26F6AD2A05C40CF5ECEC8781A3E40AA6C2C0C78A15C407ADE2DA031193E409190A6EE82A15C40819528A084183E402F3EFBBC98A15C407B76370F51173E40C4FCE2F79DA15C403470B8C130163E4098D24FAA92A15C40A825B8284A153E406DE673A0C4A15C4019137AFCF6153E40505AD1A6E5A15C40348ED4215D153E40DF88172A22A25C401788C06E29143E404523AAD021A25C4009DF4CB3E2123E40135F0C5E00A25C408BA37BF2E8113E40E6B610EA26A25C409FFC0D114F113E404FE61A9B26A25C40C18548C42E103E404A11932C26A25C40677C66249B0E3E40CE1E60B278A25C40F0EFD1761A0D3E4090AD5F6A8EA25C40CC943732AD0B3E40D6A31D2A8EA25C400CA74D8CC60A3E400C9FAD5418A35C400D70D89D9F0A3E40ECC0354223A35C4021F9E53F2C0A3E406C9535F40CA35C408F63BD577F093E407DCAEB265AA35C4092B6810FD2083E40283D75B780A35C40A4C8F3955E083E40CB8E95513EA35C404C90E32C25083E4023263A74E0A25C40AD32ABA085083E408D05089682A25C40227BAA0FE6083E4094362EC45BA25C40B59EE1DC72083E4014B22B346CA25C406E264542EC073E403B1636C092A25C4049272E9465073E40EBF09F7071A25C406E321024DF063E40F5C6428934A25C40AB5D6C3B7F063E407F19471019A25C40DD537F1719073E40BFE490DCCBA15C4064B51053C6073E404DC87CAA94A15C409820F25E13083E40C0709CA862A15C4034042AA219073E40A2D5B0FC67A15C40F6BB726759063E4040907FC9A4A15C40F863073B59063E4043ECFEA8AFA15C40330F5734AC053E40B791997AAFA15C408F76B535FF043E400C18EB6AD0A15C40824588AB2B043E40765626C6E0A15C404B73132E58033E409751DB7D12A25C405C33EDCD44033E40B74D8CA80CA25C40CFF89D7D24023E40E2E3A6F9E5A15C403E39439C24023E40F7987F29CAA15C40E6B0D3B177013E40472EAC4FAEA15C40DA3B6954A4003E402E393B617CA15C4002E1ED3FE4FF3D400AA3AD734AA15C406F14D42924FF3D40302200BA97A15C40FE04E50DD7FE3D409FBE4ECCCEA15C405F1937E329FE3D4092EE20E99CA15C409D77954090FD3D40F147EFEA5FA15C409A885BF9BCFC3D4090CF7131B8A15C40DBD5D16149FC3D408A5B519FDEA15C40DAA0829662FB3D4082E7D359D3A15C40E283C82A8FFA3D408DDBF5558BA15C4055665125CFF93D4048C101F553A15C4014BE94BC48F93D40DD9379480CA15C401D7A387ECFF93D40851660F9F0A05C404EFB052303FB3D4001CA50DBC4A05C40FF347D2350FB3D402DBC0F816CA05C4040C59BCB76FB3D4049C020304BA05C40FC86BADBC9FA3D4096D1E6C145A05C402902CBFC29FB3D40A2205407E89F5C40E7570B6AEAFB3D40EE5C28A4849F5C405C5EC54524FC3D40AB3559687F9F5C4094E889D957FD3D4014C9B94E699F5C400FF66CE357FD3D40F5316EAE059F5C404CC922D297FC3D400FCCE4DB059F5C403BB6AE0C58FD3D406517BE53329F5C40C7BD9A5278FE3D40C838C3CE169F5C40335152B3EBFE3D40E2528210DA9E5C40D3DBF53C12FF3D4053025BEAA29E5C40B70C5DA685FF3D404A276922719E5C4016E2060B4CFF3D40B0262FBA239E5C402717957612FF3D40EEC3D3810D9E5C406BFB40ED8BFE3D404BC15B2A4A9E5C400908814D05FE3D40DE95450B559E5C403955FC0F45FD3D40E60BFE2A189E5C40E62C42CAD1FC3D40EC4DEEBAF19D5C40C704F3F2DEFD3D40E7AC5E52D69D5C404D4140DED8FE3D4053ED28BEA49D5C4087884DEA85FF3D40B17CD7427E9D5C40C156CE9C6C003E40F527115E4C9D5C401E769E6BACFF3D40229E90AA0F9D5C408EF849900C003E40FFA0F75AC29C5C400A21364346003E40C5370F66969C5C400AE5FDD479013E40898671CB6F9C5C4077C1C9F2D9013E40C7FBE928339C5C408946222D9A023E404CC71859019C5C40E226F40F3A023E404DA86DF7B39B5C401E599ED326023E40DFB28C04A99B5C40F9530861AD023E406C694E75249B5C40159F436F0D033E409FC81023C19A5C40F54E4BCFE0033E40F998EC74479A5C406C8998255A033E40F3D64997529A5C40D707987DCD033E40070E0260639A5C40309BD4D5ED043E407403D6971B9A5C402F9131DE4D053E408CB541B0C8995C406BB6BEC44D053E4065E9EF0F97995C40F9120FB3FA053E40FE4C834F4F995C40825DF45D94063E4046CFD739C5985C40F86A0FE82D073E4056B2340D3B985C407871EBDA40073E408687B5A8D7975C40D5516DA0ED073E40627A4D6F42975C40832BDDB213083E401DE5DA90D9965C40F0FFCABA33093E406454C6BB91965C40C984832E6D093E4048779B9C28965C4015C239DDBF083E40CF04453893955C40F75C140A9F073E40585FB384F8945C400A38F53C38083E40682C0E99B0945C4096BC7468B1073E40E350556C52945C40F12A1F7BD0053E401176236D96935C40B8CCCA6F0F053E4092325D7BE5925C407D2F3FED27043E403408E73C66925C40614D9BD6A6023E40C7A3FEC3D08E5C406DB18DD126003E40DA164FD0678E5C40274E7FB90C013E401E947CC6168D5C40A8151A03B1023E408B2281803D8D5C406393723558043E405554766B1C8D5C4025C16E7992073E4021F636D0978C5C406D06023D920A3E4056746744298C5C402D676DB8110C3E40919D31F0E68B5C40031A51C8A40D3E406EC780B20D8C5C406AAABDFD5F123E40C24F198DEC8B5C408D597D06E7153E405969B1B8AF8B5C40A830F4C0B3173E403AB7B68F378A5C40FAC2C9425D183E4018F0677C2C8A5C40DDB732707D193E4083C968113D8A5C40BDAD34C1EA1A3E40377904E2C8895C40ABF81048231B3E407B5EB865CE895C40C1A8E0D4561C3E40AC03D6C7BD895C401B3E7AF1761D3E40426B34C4BD895C40A191578F5D1E3E402503775B28895C40646DF827BC1E3E40495619A55F895C406141387810213E404C67B17E54895C408711C7E10A253E403566BA0E12895C405ADF7529B7253E40A87EFBCFF0885C401DFECEB910273E4002EE8ACFA8885C40EBE04EE269283E405415FFA84A885C406FECC15B9C293E40962CF8D723885C4020DD1223692B3E40DD1AD47667875C40B7008CB9672E3E4077E12C561F875C40DF89DB8A67313E401337D839D7865C40D724DE2EA7333E40E0F69C4E9A865C40A853590E80333E40C7F62F435D865C40885E8A5D99353E404BC5EB063C865C4024F134FA98353E40FDD85797B1855C4082105830D7343E408BE4DCD94D855C405060667C5C353E401084E0AEB2845C4060C27B2441363E40B4CA8B840C845C40B04F866305363E408F31B64E13835C40DE8CC92E55353E4059B09D8CE1825C40F9D40EB85A343E40555FFF37AA825C40410DAB3FC0333E40861795E52A825C4063EB049011333E40E0BC81A714825C40A4115B9EE4333E40861E993AE8815C407E851602F1343E40B1B7C94BFE815C407CA18CAEC4353E408D46DB22F3815C40A0ED22AC84363E4049E96ADB19825C40EA9728B70B373E40FF6D020E78825C40DCE3135FD3363E409A22CDD1B4825C4003C57D228E383E40D373680D1E835C4011E27069DC383E404127877AB3835C40941EDA86AB3A3E40B5EF705A43845C40141806CDED3C3E40EB55F202BD845C4058A540BB3C403E40F1F483B736855C406021D02E65433E40C6341EE16D855C405F14301E60473E404D09855F94855C40555A54242E4C3E409A31B603C6855C4040C3999062503E400517EFB0EC855C40006EBBC4C9523E408E161EDD4A865C40F3F878FAF7543E40EA6CDA4CCE865C40085A0F1025573E401608D62619875C40FFB07E2321583E4080666D373C875C40ADFE43C21C593E40B936BD596D875C4065B2E7F79E593E406185C503E0875C408356C157935A3E40F6AF1E7F1A885C40D5129ED1BF5B3E409108F049BE885C40D1624B32B35E3E40A6B7ECD2CD895C402973B01F0C633E4087BABCE5428A5C400CCF9EC40B653E40E36AD146B98A5C407BC07B323E673E40A5E128695C8B5C40DE10FCD9BC653E40BD18DEC4888B5C40A20285F948653E4073684841C58B5C400126B33CD5643E40B7F66F9CF18B5C404D193D76A2643E40A3E22637138C5C40A537C2CC94643E4060EBE4461B8C5C409C9483744A643E40494E892A368C5C40635D144EBA643E407835BA6E568C5C401FDE9C3E1C653E40CB6E94C9578C5C407A59F749D6653E40BD1BB334618C5C4080967D3D5D663E4048329EE7638C5C401176E6B004673E40A03B9B526D8C5C4065E1875782673E40C983A715788C5C408611DD65ED673E40D65E6F1BA38C5C40646FFEA809683E40E787FC76CF8C5C40B3A887A9B1673E40C4DFFCFFE88C5C40C3190E3450673E4072BF220CF18C5C4082F645557A663E40A3C54007F18C5C40D5A31BBF9F653E40A1A9FDAAEF8C5C40F8A0BB5AEA643E401679A751198D5C40FAE783B422643E401C00B1B6228D5C405F16DB4C89633E400A18D022308D5C4060D9CCB8CA623E401D0D5C99418D5C4055DCB0D76D623E406A0AEED25D8D5C4048FBEB6969623E400EC3F3265F8D5C40FB641A3FD9613E40C7D6BA33678D5C407BF04A1557613E407224E8F0718D5C402C9401E5E2603E40D94F0AAF7C8D5C40286224E993603E405BA3C92F928D5C403F3E151494603E406C65BAFEA48D5C406A713F6A5C603E40899FCDABA78D5C40C9FC6DC3FA5F3E40CF623234E88D5C404D419899BE603E402980E901498E5C407992F014CD613E406F913DB1478E5C40662350C28B623E4074FFA197378E5C40D81A4CFA4E633E40081AE8C54B8E5C400B36235AD1633E40373EBC94858E5C4059C5673C0E643E4042D4E95CBB8E5C40004D724A70643E40B34A52ABB48E5C408AFF1C5F0E653E402E145DCD958E5C40B19163733C663E4080405DEE998E5C403E88C17986683E408B301E358B8E5C40FD305B53166A3E40F58F0BCCC38E5C4004643D53D06C3E40FDE54E92F58E5C403643954A406D3E401343C8002A8F5C40B436AE8CFF6C3E40676C081D618F5C400C9E7E50906C3E406A400E00808F5C409EF8BE8CC86B3E407D828CD7968F5C40FF404BA4796B3E4019A553F9CD8F5C40A22E0DF6876B3E40F0C0C6DDE88F5C40700C3323886B3E40B17B9C85EB8F5C40E2B5C155F36A3E406F27B4592D905C40B5836793066A3E40EFAB03356B905C406971182C2C6A3E401027AB2C8E905C40B3C65798516A3E4010A799A097905C402B9676C6EF6A3E4032F5E8079D905C400E5B1079516B3E40E97E097FF4905C4036E5FED4436C3E400E134F1639915C40DE3020BE726C3E404F99A57259915C407BD4BF37A16D3E40B08CBF5D70915C40052E33AB646E3E4044E175C698915C406BF622D23A6F3E409345ECA3A7915C405E4E7A6D23703E40FF8E9B8CE1915C40EDD85F381A713E4036606DB2E5915C40FB4642AC7B723E40487D78F1FD915C40FB6CE469EB723E4092242FAD27925C40657E439856733E40B32855F047925C40F55E04501A733E409661CDFD72925C406D24817036733E40D9D20B8688925C4000B3011A57733E400EBF8442BA925C405757EC58FA723E409AB9499BE6925C409939AFF58A723E408452858205935C40AA3467C132723E40E2600D071F935C408A7B1792CC713E4031251DF93D935C40754F069FE8713E40E7DA5E7C57935C407A97E12179713E4079A70FD35C935C401DF102330E713E40315CB55576935C402A3E45B59E703E401C6D172889935C40948E7C318C703E402C35E5BD8B935C40B4627421836F3E40B339262199935C40BD2B92B9E96E3E40F9556D2CC4935C4091CB5C2C016F3E40DFCB53B12F945C409EC19E86636E3E40784C2B2D3D945C404CE1C54AB76E3E40EC2FBAD189945C40D99AFAB49B6E3E40F1A050EB1A955C40B9AB5EA4726D3E40289016D316955C407F7A4A69F06C3E40A24C1D90C9955C406BEA6B201B6C3E4046E6C89F23965C40AB9DEAF7DE6B3E40D949411E83965C40EE23A4C50D6C3E4000E7CE68BE965C40AA6BD179F66C3E40AD3DD533D4965C403FA7A471F16E3E40256D91FDE1965C406E69B2FD5B713E40DF0FED1C15975C40C2C71A6273713E4038B78CED0F975C40DE336D25D0723E40544F6FB602975C40542BD94977743E404EEF0889EE965C404D1C863B77743E403AEA62E4D7965C40B64E836410763E40CD6658BAE2965C40D33C624797763E40404DAE16DC965C404254105E35773E40B4FF67950C975C40E7376A1BA5773E40188E770131975C40A10BB34251783E401812DE7649975C40A5567F7CF8793E40933531ED65975C4085A4779D5E7B3E4076C6F0C78F975C40D74DB785507C3E40F9558471B5975C40469896B6347C3E400668EFCD0C985C404F112136847B3E40318F4F1EFF975C40991176E0067A3E40B9D4BCB109985C40EEF9C157CF783E402C5A8C0F32985C408C5F3A14D4783E40210105C453985C40A9D9B5C043793E4059B4AFD163985C408A0216FBAE783E405F1C32338C985C40757F27F6CA783E40C6FF612EC5985C4091ADF06EAE7B3E405108D874DD985C4024307D2D027C3E405DE0050BFF985C4016C5F388AE7B3E4086DF4FF306995C404C2CB6CBAE7A3E401593BE6C1C995C40638D32215B7A3E40E7CC83F012995C409039D0CFF4793E4043C30D6F2C995C40DD4237E689793E405ACC997F25995C40E36343AE4D783E4008AA3F7C2D995C40F3D6167DCB773E405C3EA57F73995C404460B7A51A783E404ACBFC78B9995C40DAA33F582D783E4054A478D8F8995C401A56B161F5783E40665F5133119A5C40593F71B6B8793E40D75FBDCB1E9A5C40535802AF807A3E40E08152E1499A5C40A42405EEA57A3E406F6CDCE7459A5C404BC5A846FE7A3E404471812C3B9A5C40E60405C42C7B3E409F0A97463B9A5C40340399EABC7B3E40956E3702559A5C40502FB971A57C3E40D23F433B849A5C403C4A9B89517D3E40A5AED8DF999A5C401344D201EB7D3E40E963CEF2959A5C400BCC8F73847E3E40922FDEB9BF9A5C401D781E89D37E3E403C90108AED9A5C40026408F71D7F3E40E3642548429B5C40D0CEF990E17E3E407628F52D809B5C40F636F3A4D37E3E401B1A394CCA9B5C40C5587636517F3E40D137068C119C5C408B3D87ECEA7E3E40CCE1C2D8589C5C40CFB53FB9C57E3E40685AA2018C9C5C405CDEB4F7DC7E3E40900BD6B0AD9C5C40A6F9F4740B7F3E404CC2FEC5E49C5C4083DE2531977E3E4067B14DCAEC9C5C40CD0DD970517E3E4048D2526F0E9D5C4066DC2C6D517E3E40E18AA29E1E9D5C40CA2E60447B7E3E40FFB0433A259D5C4099CBB61DEB7D3E40D52427722A9D5C40267656D0277D3E407D672B52459D5C40A1A28E4CF97C3E40E0C1577E3E9D5C40C4C0C50D857C3E40B9596607609D5C4008EC4D7B077C3E40485A3458DE9D5C409BA3336F3F7B3E40E8A1286DFA9D5C40B644D074777A3E40C72F442CEE9D5C40F73F7EB6D4793E408314F43DDB9D5C402AC14AC769793E4076D4D7D2D99D5C40BA8ECA1316793E4080E66E8DC19D5C40139DC5A5D9783E4026D28273C19D5C404E43776465783E40DFA6729CDD9D5C40EDAE5E6AFA773E402F86BADCE29D5C40BDE6D29A65773E407123AB220F9E5C4076A27B0EDA763E406D79BE94479E5C4004FDDFE498763E4022168DE6549E5C404CF34F1204763E409004E418719E5C405D172D96C7753E40AADCD325909E5C40708B6D7440763E40DB41D895A19E5C406E392CA108763E40CF16561FD29E5C40FF2899D17C763E40DC6EB0BE129F5C4036C7B3E0AF763E4039B09B6E299F5C406C665488EC753E40B35F8ED7699F5C40D3493B5E40753E401D24E3E5889F5C40D85ED737B9753E404374C4109C9F5C403555CCF315773E406657E4E1C19F5C40B45E5D56AF773E405FC635C9E09F5C404E00BC6C85773E402C2B892C08A05C40307CE5A802793E40DF6A48FF3DA05C40F785BE3207793E4040F2D2E5B2A05C40A740CF796D783E4021020A55A4A05C40C9B0970456793E40901428AE99A05C40F38463A5C5793E4020BE7AF053A05C408B0286A8A97A3E4041DC8A9569A05C404D160DDD1D7B3E40361B3077BAA05C400FA768D3AD7B3E402CF8EDF2DAA05C40CBD27DBF677C3E40E4236860D4A05C40E094AF36017D3E40A2D513B8CDA05C4002EA90FA467D3E40C9D09FA9E0A05C40FAAF563BAD7D3E4009335E0220A15C405B2EC4110A7E3E40CA4712161CA15C4056BDCAAD797E3E40985E581627A15C40D043F87E5D7F3E40D550854B1BA15C40CFDB741295803E40788DC995FCA05C40598F30F186813E405997A229D4A05C4087982F325D813E40110D9A3A73A05C4038E1B52C46813E4011768F0215A05C40AEE6F56046813E40A35C2A88FB9F5C409A183E14A8813E402D27C24DE39F5C4009929620A8813E4003B05668E39F5C405AAE7D1213823E40D260DDDE2AA05C40C96C1F7990823E40D087DF6476A05C40042D517320833E401C326DFDAAA05C40449BFCF881833E4062F673EB2EA15C40748DB1F08A833E404741E0434BA15C4030A9BD42D5833E40B4FC4EEA5CA15C401DBF4C5B65843E402E60003C98A15C4045690AE2B8843E4084894453B3A15C40513341E556853E40B16A70CBB0A15C40C74F4B58F0853E40E66D9643B2A15C4034ADF29464863E40D7E1CF02D0A15C408FF5BC62DD863E400D869BE0F1A15C4070BCB991A0873E4005F08E8126A25C405D6837FF0F883E4048D5324A3CA25C4059BF551BEF883E40E9A1BE6257A25C40321BFE7488893E406F49C4A3A9A25C40954FCD1EF3893E40F6997FAB1AA35C402C3EE2F9AC893E40'}
    file_name = jInfo['layer']
    values = jInfo['content']
    field_str=' ('
    value_str=' ('
    for i,k in enumerate(values):
        field_str = field_str+k+','
        value_str = value_str+"'"+values[k]+"'"+','
    field_str=field_str[:-1]+')'
    value_str=value_str[:-1]+')'
    query1 = "INSERT INTO "+file_name+field_str+' VALUES'+value_str+';'
    try:
        cur.execute(query1)
        conn.commit()
    except Exception as e:
        return '0'

    query2 = "SELECT * from "+file_name+';'
    cur.execute(query2)
    rows = cur.fetchall()
    fields = cur.description
    conn.commit()

    rowList=[]
    for i in range(len(rows)):
        rowList.append(list(rows[i][0:-1]))  # remove geom column
    fields = fields[:-1]  # remove geom field
    column_list = []
    for i in fields:
        column_list.append({'text':i[0],'value':i[0]})  # decompose tuple
    row_list = []
    for row in rows:
        tmp_result = {}
        for i in range(len(column_list)):
            tmp_result[column_list[i]['text']] = row[i]
        row_list.append(tmp_result)

    # 输出格式一
    json_dic = {}
    json_dic['title'] = column_list
    json_dic['content'] = row_list
    jsondata=json.dumps(json_dic, ensure_ascii=False)

    # print("Write to file successfully")
    return jsondata


# query
# http://49.232.75.144:9423/dogis/api/v1.0/query
@app.route('/dogis/api/v1.0/query', methods=['POST'])
def query():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['sql']='select class_5,cost from subwayline'
    query = jInfo['sql']
    sql_part = query.split(' ')
    for i,p in enumerate(sql_part):
        if p == 'from':
            table_name = sql_part[i+1]
            break
    try:
        condition_str = query[query.index('where'):]
    except:
        condition_str = ''

    # try:
    #     cur.execute(query)
    # except Exception as e:
    #     return '0'
    # rows = cur.fetchall()
    # fields = cur.description 
    query_field = query
    try:
        cur.execute(query_field)
    except:
        return '0'    
    cur_fields = cur.description
    cur_rows = cur.fetchall()
    field_str=""
    for field in cur_fields:
        if field == 'geom':
            continue
        field_str=field_str+field.name+","
    field_str=field_str[:-1]
    query_tmp = "SELECT \
                row_to_json(fc) \
                FROM ( \
                    SELECT \
                        'FeatureCollection' AS type \
                        , array_to_json(array_agg(f)) AS features \
                    FROM ( \
                        SELECT \
                            'Feature' AS type \
                            , ST_AsGeoJSON(geom)::json as geometry \
                            , ( \
                                SELECT \
                                    row_to_json(t) \
                                FROM ( \
                                    SELECT "+field_str+"\
                                    ) AS t \
                                ) AS properties \
                        FROM "+table_name+" "+condition_str+" \
                    ) AS f \
                ) AS fc" 
    cur.execute(query_tmp)
    cur_geojson = cur.fetchall()
    conn.commit()

    rowList=[]
    for i in range(len(cur_rows)):    
        rowList.append(list(cur_rows[i][0:-1]))  # remove geom column
    cur_fields = cur_fields[:-1]  # remove geom field
    column_list = []
    for i in cur_fields:
        column_list.append({'text':i[0],'value':i[0]})  # decompose tuple
    row_list = []
    for row in cur_rows:
        tmp_result = {}
        for i in range(len(column_list)):
            tmp_result[column_list[i]['text']] = row[i]
        row_list.append(tmp_result)

    # 输出格式一
    json_dic = {}
    json_dic['title'] = column_list
    json_dic['content'] = row_list
    # jsondata=json.dumps(json_dic, ensure_ascii=False)

    return {'geojson':cur_geojson[0][0],'attr_table':json_dic}

# uploadgeojson
# http://49.232.75.144:9423/dogis/api/v1.0/uploadgeojson
@app.route('/dogis/api/v1.0/uploadgeojson', methods=['POST'])
def uploadgeojson():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['layername']='testaccount1'
    # jInfo['userpassword'] = '12345678'
    file_name = jInfo['name']
    content = jInfo['data']
    # with open("predicted_set.geojson",encoding='utf-8') as geojson1:
    # poly1=json.load(content)
    poly1 = content

    infoList = []
    geomList=[]
    fields = ['gid'] #  initial gid field
    for i in range(len(poly1['features'])):
        polyInfo=poly1['features'][i]['properties']
        polyshape = shapely.geometry.asShape(poly1['features'][i]['geometry'])
        if i==0:
            geomtype = polyshape.geom_type
        polyValues=[i]  # initial index
        if polyInfo:
            for k,v in polyInfo.items():
                if i == 0:
                    fields.append(k)
                polyValues.append(v)
        else:
            pass

        infoList.append(polyValues)
        geomList.append(polyshape.wkt)

    create_str = 'CREATE TABLE '+file_name+"("
    for i in range(len(fields)):
        type_str=str(type(infoList[0][i]))
        sql_type = type_str[type_str.index('class')+7:-2]
        if sql_type == 'str':   # sql 不识别str
            sql_type = 'text'
        create_str = create_str+fields[i]+" "+sql_type+" NULL, "
        # create_str = create_str+f+" int, "
    create_str = create_str+"PRIMARY KEY("+fields[0]+"));"
    query1 = create_str
    try:
        cur.execute(query1)
    except Exception as e:
        return '0'
    conn.commit()
    # add spatial
    spatial_str="SELECT AddGeometryColumn('"+file_name+"', 'geom', 4327, '"+'geometry'+"', 2 );"
    query2 = spatial_str
    cur.execute(query2)
    conn.commit()
    # INSERT INTO  table_name  VALUES (value1,value2,value3,...)，(value1,value2,value3,...);
    value_str='('
    for i in range(len(infoList)):
        for v in infoList[i]:
            str_v = str(v)
            if str_v == 'None':
                str_v = 'NULL'
                value_str = value_str+str_v+","
            else:            
                value_str=value_str+"'"+str_v +"',"
        if polyInfo:
            value_str=value_str+"ST_GeomFromEWKT('"+geomList[i]+"')),("
        else:
            value_str=value_str+"ST_Transform(st_geometryfromtext('"+geomList[i]+"',3857),4327)),("
    value_str = value_str[:-2]
    query3 = "INSERT INTO " + file_name + " VALUES "+ value_str+";"
    cur.execute(query3)
    conn.commit()
    # query4 = "SELECT ST_AsText(ST_Transform(st_geometryfromtext('POINT(120.8 20.5)',4326),900913));"

    return '1'


# register user
# http://49.232.75.144:9423/dogis/api/v1.0/register
@app.route('/dogis/api/v1.0/users/register', methods=['POST'])
def register():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['useraccount']='testaccount1'
    # jInfo['userpassword'] = '12345678'
    useraccount = jInfo['email']
    userpassword = jInfo['password']
    nickname = jInfo['name']
    query1 = "INSERT INTO platform_user (useraccount,userpassword,nickname) values ('"+useraccount+"','"+userpassword+"','"+nickname+"');"
    try:
        cur.execute(query1)
        conn.commit()
    except Exception as e:
        return '0'

    return '1'

# LOGIN user
# http://49.232.75.144:9423/dogis/api/v1.0/login
@app.route('/dogis/api/v1.0/users/login', methods=['POST'])
def login():
    jInfo = request.get_json()
    # jInfo={}
    # jInfo['useraccount']='testaccount1'
    # jInfo['userpassword'] = '1234567'
    useraccount = jInfo['email']
    userpassword = jInfo['password']
    query1 = "SELECT useraccount FROM platform_user WHERE useraccount='"+useraccount+"';"
    cur.execute(query1)
    rows = cur.fetchall()
    conn.commit()
    if len(rows) == 0:
        return '0'

    query2 = "SELECT useraccount FROM platform_user WHERE useraccount='"+useraccount+"' and userpassword ='"+userpassword+"';"
    cur.execute(query2)
    rows2 = cur.fetchall()
    conn.commit()
    if len(rows2) == 0:
        return '1'
    
    return '2'


# http://49.232.75.144:9423/dogis/api/v1.0/getTIN
@app.route('/dogis/api/v1.0/getTIN', methods=['GET'])
def getTIN():
    # jInfo = request.get_json()
    jInfo={}
    jInfo['layer']='poi'
    file_name = jInfo['layer']
    linejson=TIN.getTIN1(file_name)
    return linejson

@app.route('/dogis/api/v1.0/Convexity', methods=['POST'])
def Convexity():
    """对多边形各点进行凹凸性判断
    Args:
        data (list): 封闭图形点集
    Returns:
        [list]: 多边形中凹点坐标集合
    """
    polygon  = request.get_json()['polygon']
    area = 0.0
    last_area =0.0
    num = len(polygon)
    for i in range(0,len(polygon)):
        x1 = polygon[i][0]
        y1 = polygon[i][1]
        x2 = polygon[(i + 1) % num][0]
        y2 = polygon[(i + 1) % num][1]
        x3 = polygon[(i + 2) % num][0]
        y3 = polygon[(i + 2) % num][1]
        area = x1 * y2 + x2 * y3 + x3 * y1 - x1 * y3 - x2 * y1 - x3 * y2
        if (area * last_area) < 0:
            return 'True'
        last_area = area
    return 'False'
'''with open('./test_json/wuhan_json.txt','w+') as f:
    for row in rows:
        tmp_result = {}
        for i in range(len(column_list)):
            tmp_result[column_list[i]] = row[i]
        jsondata=json.dumps(tmp_result,ensure_ascii=False) 
        f.write(jsondata + '\n')
f.close()  '''

'''with open('./test_json/json1.txt','w+') as f:
    f.write(jsondata + '\n')    # 写入文件
f.close()'''

@app.route('/dogis/api/v1.0/getposition', methods=['POST'])
def getposition():
    data = request.get_json()
    polygon = data['polygon']
    point = data['point']
    #######################
    flag = 1
    num = len(polygon)
    for i in range(0,num):
        if (point[0] == polygon[i][0] and point[1] == polygon[i][1]) or (point[0] == polygon[(i + 1) % num][0] and point[1] == polygon[(i + 1) % num][1]):
            return 0
        if (point[1]>=polygon[i][1] and  point[1] < polygon[(i+1)%num][1]) or (point[1]>=polygon[(i+1)%num][1] and  point[1] < polygon[i][1]):
            x = (polygon[i][0] - polygon[(i + 1) % num][0]) * (point[1] - polygon[i][1]) /(float) (polygon[i][1] - polygon[(i + 1) % num][1]) + polygon[i][0]
            if (abs(x-point[0]))<1e-4:
                return 0
            if x>point[0]:
                flag = 1-flag
    return  str(flag)

@app.route('/dogis/api/v1.0/cal_polygonarea', methods=['POST'])
# def cal_polygonarea():
#     polygon = request.get_json()
#     #######################
#     # code
#     return area

def cal_polygonarea():
    '''计算多边形面积值
       points:多边形的点集，每个点为Point类型
       返回：多边形面积'''
    area = 0.0
    polygon  = request.get_json()['polygon']
    num = len(polygon)
    for i in range(0,len(polygon)):
        area += (polygon[i][0] * polygon[(i + 1)%num][1] - polygon[i][1] * polygon[(i + 1) % num][0])
    area = abs(area/2)/1000
    return {'area':str(area)} 

def ifintersect(p1,p2,p3,p4):
    if p2[0] == p1[0] or p3[0] == p4[0]:
        return False
    k1 = (float)(p2[1] - p1[1]) / (p2[0] - p1[0])
    k2 = (float)(p3[1] - p4[1]) / (p3[0] - p4[0])
    b1 = p1[1] - k1 * p1[0]
    b2 = p3[1] - k2 * p3[0]
    delta_x = (b2 - b1) / (k1 - k2)
    delta_y = delta_x * k2 + b2
    if delta_y > min(p3[1], p4[1]) and delta_y < max(p3[1], p4[1]):
        return True
    else:
        return False
@app.route('/dogis/api/v1.0/isvalid', methods=['POST'])
def isvalid():
    polygon = request.get_json()['polygon']
    #######################
    # code
    num = len(polygon)
    if num<3:
        return '-1'
    for i in range(0,num-3):
        for j in range(i+2,num-1):
            if i==0 and j==num-1:
                continue
            if ifintersect(polygon[i], polygon[i + 1], polygon[j], polygon[(j + 1)%num]):
                return '-1'

    return '1' 

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0',port=9423)
