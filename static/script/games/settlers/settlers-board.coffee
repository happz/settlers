window.settlers = window.settlers or {}
window.settlers.board_defs = window.settlers.board_defs or {}
window.settlers.board_defs.active_nodes_map_negative = { n1: false, n2: false, n3: false, n4: false, n5: false, n6: false, n7: false, n8: false, n9: false, n10: false, n11: false, n12: false, n13: false, n14: false, n15: false, n16: false, n17: false, n18: false, n19: false, n20: false, n21: false, n22: false, n23: false, n24: false, n25: false, n26: false, n27: false, n28: false, n29: false, n30: false, n31: false, n32: false, n33: false, n34: false, n35: false, n36: false, n37: false, n38: false, n39: false, n40: false, n41: false, n42: false, n43: false, n44: false, n45: false, n46: false, n47: false, n48: false, n49: false, n50: false, n51: false, n52: false, n53: false, n54: false }
window.settlers.board_defs.active_nodes_map_positive = { n1: true, n2: true, n3: true, n4: true, n5: true, n6: true, n7: true, n8: true, n9: true, n10: true, n11: true, n12: true, n13: true, n14: true, n15: true, n16: true, n17: true, n18: true, n19: true, n20: true, n21: true, n22: true, n23: true, n24: true, n25: true, n26: true, n27: true, n28: true, n29: true, n30: true, n31: true, n32: true, n33: true, n34: true, n35: true, n36: true, n37: true, n38: true, n39: true, n40: true, n41: true, n42: true, n43: true, n44: true, n45: true, n46: true, n47: true, n48: true, n49: true, n50: true, n51: true, n52: true, n53: true, n54: true }
window.settlers.board_defs.active_paths_map_negative = { p1: false, p2: false, p3: false, p4: false, p5: false, p6: false, p7: false, p8: false, p9: false, p10: false, p11: false, p12: false, p13: false, p14: false, p15: false, p16: false, p17: false, p18: false, p19: false, p20: false, p21: false, p22: false, p23: false, p24: false, p25: false, p26: false, p27: false, p28: false, p29: false, p30: false, p31: false, p32: false, p33: false, p34: false, p35: false, p36: false, p37: false, p38: false, p39: false, p40: false, p41: false, p42: false, p43: false, p44: false, p45: false, p46: false, p47: false, p48: false, p49: false, p50: false, p51: false, p52: false, p53: false, p54: false, p55: false, p56: false, p57: false, p58: false, p59: false, p60: false, p61: false, p62: false, p63: false, p64: false, p65: false, p66: false, p67: false, p68: false, p69: false, p70: false, p71: false, p72: false, p73: false }

window.settlers.board_defs.nodes =
  n1:
    neighbours:			[2, 6]
    fields:			[1]
    paths:			[1, 3]
  n2:
    neighbours:			[1, 3]
    fields:			[1]
    paths:			[1, 2]
  n3:
    neighbours:			[2, 4, 7]
    fields:			[1, 2]
    paths:			[2, 4, 5]
  n4:
    neighbours:			[3, 5, 10]
    fields:			[1, 2, 5]
    paths:			[4, 15, 16]
  n5:
    neighbours:			[6, 16, 4]
    fields:			[1, 4, 5]
    paths:			[13, 14, 15]
  n6:
    neighbours:			[1, 15, 5]
    fields:			[1, 4]
    paths:			[3, 12, 13]
  n7:
    neighbours:			[3, 8]
    fields:			[2]
    paths:			[5, 6]
  n8:
    neighbours:			[7, 9, 11]
    fields:			[2, 3]
    paths:			[6, 7, 8]
  n9:
    neighbours:			[8, 10, 14]
    fields:			[2, 3, 6]
    paths:			[7, 18, 19]
  n10:
    neighbours:			[4, 19, 9]
    fields:			[2, 5, 6]
    paths:			[16, 17, 18]
  n11:
    neighbours:			[8, 12]
    fields:			[3]
    paths:			[8, 9]
  n12:
    neighbours:			[11, 13]
    fields:			[3]
    paths:			[9, 10]
  n13:
    neighbours:			[12, 14, 23]
    fields:			[3, 7]
    paths:			[10, 21, 22]
  n14:
    neighbours:			[9, 21, 13]
    fields:			[3, 6, 7]
    paths:			[19, 20, 21]
  n15:
    neighbours:			[6, 18]
    fields:			[4]
    paths:			[11, 12]
  n16:
    neighbours:			[5, 17, 20]
    fields:			[4, 5, 9]
    paths:			[14, 28, 29]
  n17:
    neighbours:			[18, 27, 16]
    fields:			[4, 8, 9]
    paths:			[26, 27, 28]
  n18:
    neighbours:			[15, 26, 17]
    fields:			[4, 8]
    paths:			[11, 25, 26]
  n19:
    neighbours:			[10, 20, 22]
    fields:			[5, 6, 10]
    paths:			[17, 31, 32]
  n20:
    neighbours:			[16, 30, 19]
    fields:			[5, 9, 10]
    paths:			[29, 30, 31]
  n21:
    neighbours:			[14, 22, 25]
    fields:			[6, 7, 11]
    paths:			[20, 34, 35]
  n22:
    neighbours:			[19, 32, 21]
    fields:			[6, 10, 11]
    paths:			[32, 33, 34]
  n23:
    neighbours:			[13, 24]
    fields:			[7]
    paths:			[22, 23]
  n24:
    neighbours:			[23, 25, 36]
    fields:			[7, 12]
    paths:			[23, 37, 38]
  n25:
    neighbours:			[21, 34, 24]
    fields:			[7, 11, 12]
    paths:			[35, 36, 37]
  n26:
    neighbours:			[18, 29]
    fields:			[8]
    paths:			[24, 25]
  n27:
    neighbours:			[17, 28, 31]
    fields:			[8, 9, 13]
    paths:			[27, 43, 44]
  n28:
    neighbours:			[29, 41, 27]
    fields:			[8, 13]
    paths:			[40, 42, 43]
  n29:
    neighbours:			[26, 28]
    fields:			[8]
    paths:			[24, 40]
  n30:
    neighbours:			[20, 31, 33]
    fields:			[9, 10, 14]
    paths:			[30, 46, 47]
  n31:
    neighbours:			[27, 39, 30]
    fields:			[9, 13, 14]
    paths:			[44, 45, 46]
  n32:
    neighbours:			[22, 33, 35]
    fields:			[10, 11, 15]
    paths:			[33, 49, 50]
  n33:
    neighbours:			[30, 42, 32]
    fields:			[10, 14, 15]
    paths:			[47, 48, 49]
  n34:
    neighbours:			[25, 35, 38]
    fields:			[11, 12, 16]
    paths:			[36, 52, 53]
  n35:
    neighbours:			[32, 44, 34]
    fields:			[11, 15, 16]
    paths:			[50, 51, 52]
  n36:
    neighbours:			[24, 37]
    fields:			[12]
    paths:			[38, 39]
  n37:
    neighbours:			[36, 38]
    fields:			[12]
    paths:			[39, 41]
  n38:
    neighbours:			[34, 46, 37]
    fields:			[12, 16]
    paths:			[53, 54, 41]
  n39:
    neighbours:			[31, 40, 43]
    fields:			[13, 14, 17]
    paths:			[45, 57, 58]
  n40:
    neighbours:			[41, 50, 39]
    fields:			[13, 17]
    paths:			[56, 57, 72]
  n41:
    neighbours:			[28, 40]
    fields:			[13]
    paths:			[42, 72]
  n42:
    neighbours:			[33, 43, 45]
    fields:			[14, 15, 18]
    paths:			[48, 60, 61]
  n43:
    neighbours:			[39, 48, 42]
    fields:			[14, 17, 18]
    paths:			[58, 59, 60]
  n44:
    neighbours:			[35, 45, 47]
    fields:			[15, 16, 19]
    paths:			[51, 63, 64]
  n45:
    neighbours:			[42, 51, 44]
    fields:			[15, 18, 19]
    paths:			[61, 62, 63]
  n46:
    neighbours:			[38, 47]
    fields:			[16]
    paths:			[54, 55]
  n47:
    neighbours:			[44, 53, 46]
    fields:			[16, 19]
    paths:			[55, 64, 65]
  n48:
    neighbours:			[43, 49, 52]
    fields:			[17, 18]
    paths:			[59, 67, 68]
  n49:
    neighbours:			[50, 48]
    fields:			[17]
    paths:			[66, 67]
  n50:
    neighbours:			[40, 49]
    fields:			[17]
    paths:			[56, 66]
  n51:
    neighbours:			[45, 52, 54]
    fields:			[18, 19]
    paths:			[62, 69, 70]
  n52:
    neighbours:			[48, 51]
    fields:			[18]
    paths:			[68, 69]
  n53:
    neighbours:			[47, 54]
    fields:			[19]
    paths:			[65, 71]
  n54:
    neighbours:			[51, 53]
    fields:			[19]
    paths:			[70, 71]

window.settlers.board_defs.paths =
  p1:
    nodes:			[1, 2]
  p2:
    nodes:			[2, 3]
  p3:
    nodes:			[1, 6]
  p4:
    nodes:			[3, 4]
  p5:
    nodes:			[3, 7]
  p6:
    nodes:			[7, 8]
  p7:
    nodes:			[8, 9]
  p8:
    nodes:			[8, 11]
  p9:
    nodes:			[11, 12]
  p10:
    nodes:			[12, 13]
  p11:
    nodes:			[15, 18]
  p12:
    nodes:			[15, 6]
  p13:
    nodes:			[6, 5]
  p14:
    nodes:			[5, 16]
  p15:
    nodes:			[5, 4]
  p16:
    nodes:			[4, 10]
  p17:
    nodes:			[10, 19]
  p18:
    nodes:			[10, 9]
  p19:
    nodes:			[9, 14]
  p20:
    nodes:			[14, 21]
  p21:
    nodes:			[14, 13]
  p22:
    nodes:			[13, 23]
  p23:
    nodes:			[23, 24]
  p24:
    nodes:			[26, 29]
  p25:
    nodes:			[18, 26]
  p26:
    nodes:			[18, 17]
  p27:
    nodes:			[17, 27]
  p28:
    nodes:			[17, 16]
  p29:
    nodes:			[16, 20]
  p30:
    nodes:			[20, 30]
  p31:
    nodes:			[20, 19]
  p32:
    nodes:			[19, 22]
  p33:
    nodes:			[22, 32]
  p34:
    nodes:			[22, 21]
  p35:
    nodes:			[21, 25]
  p36:
    nodes:			[25, 34]
  p37:
    nodes:			[25, 24]
  p38:
    nodes:			[24, 36]
  p39:
    nodes:			[36, 37]
  p40:
    nodes:			[29, 28]
  p41:
    nodes:			[37, 38]
  p42:
    nodes:			[28, 41]
  p43:
    nodes:			[28, 27]
  p44:
    nodes:			[27, 31]
  p45:
    nodes:			[31, 39]
  p46:
    nodes:			[31, 30]
  p47:
    nodes:			[30, 33]
  p48:
    nodes:			[33, 42]
  p49:
    nodes:			[33, 32]
  p50:
    nodes:			[32, 35]
  p51:
    nodes:			[35, 44]
  p52:
    nodes:			[35, 34]
  p53:
    nodes:			[34, 38]
  p54:
    nodes:			[38, 46]
  p55:
    nodes:			[46, 47]
  p56:
    nodes:			[40, 50]
  p57:
    nodes:			[40, 39]
  p58:
    nodes:			[39, 43]
  p59:
    nodes:			[43, 48]
  p60:
    nodes:			[43, 42]
  p61:
    nodes:			[42, 45]
  p62:
    nodes:			[45, 51]
  p63:
    nodes:			[45, 44]
  p64:
    nodes:			[44, 47]
  p65:
    nodes:			[47, 53]
  p66:
    nodes:			[50, 49]
  p67:
    nodes:			[48, 49]
  p68:
    nodes:			[48, 52]
  p69:
    nodes:			[52, 51]
  p70:
    nodes:			[51, 54]
  p71:
    nodes:			[54, 53]
  p72:
    nodes:			[40, 41]
