window.settlers = window.settlers or {}
window.settlers.board_defs = window.settlers.board_defs or {}
window.settlers.board_defs.active_nodes_map_negative = [ null, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false ]
window.settlers.board_defs.active_nodes_map_positive = [ null, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true, true ]
window.settlers.board_defs.active_paths_map_negative = [ null, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false ]

window.settlers.board_defs.nodes = [
  null,
  {
    neighbours:			[2, 6]
    fields:			[1]
    paths:			[1, 3]
  },
  {
    neighbours:			[1, 3]
    fields:			[1]
    paths:			[1, 2]
  },
  {
    neighbours:			[2, 4, 7]
    fields:			[1, 2]
    paths:			[2, 4, 5]
  },
  {
    neighbours:			[3, 5, 10]
    fields:			[1, 2, 5]
    paths:			[4, 15, 16]
  },
  {
    neighbours:			[6, 16, 4]
    fields:			[1, 4, 5]
    paths:			[13, 14, 15]
  },
  {
    neighbours:			[1, 15, 5]
    fields:			[1, 4]
    paths:			[3, 12, 13]
  },
  {
    neighbours:			[3, 8]
    fields:			[2]
    paths:			[5, 6]
  },
  {
    neighbours:			[7, 9, 11]
    fields:			[2, 3]
    paths:			[6, 7, 8]
  },
  {
    neighbours:			[8, 10, 14]
    fields:			[2, 3, 6]
    paths:			[7, 18, 19]
  },
  {
    neighbours:			[4, 19, 9]
    fields:			[2, 5, 6]
    paths:			[16, 17, 18]
  },
  {
    neighbours:			[8, 12]
    fields:			[3]
    paths:			[8, 9]
  },
  {
    neighbours:			[11, 13]
    fields:			[3]
    paths:			[9, 10]
  },
  {
    neighbours:			[12, 14, 23]
    fields:			[3, 7]
    paths:			[10, 21, 22]
  },
  {
    neighbours:			[9, 21, 13]
    fields:			[3, 6, 7]
    paths:			[19, 20, 21]
  },
  {
    neighbours:			[6, 18]
    fields:			[4]
    paths:			[11, 12]
  },
  {
    neighbours:			[5, 17, 20]
    fields:			[4, 5, 9]
    paths:			[14, 28, 29]
  },
  {
    neighbours:			[18, 27, 16]
    fields:			[4, 8, 9]
    paths:			[26, 27, 28]
  },
  {
    neighbours:			[15, 26, 17]
    fields:			[4, 8]
    paths:			[11, 25, 26]
  },
  {
    neighbours:			[10, 20, 22]
    fields:			[5, 6, 10]
    paths:			[17, 31, 32]
  },
  {
    neighbours:			[16, 30, 19]
    fields:			[5, 9, 10]
    paths:			[29, 30, 31]
  },
  {
    neighbours:			[14, 22, 25]
    fields:			[6, 7, 11]
    paths:			[20, 34, 35]
  },
  {
    neighbours:			[19, 32, 21]
    fields:			[6, 10, 11]
    paths:			[32, 33, 34]
  },
  {
    neighbours:			[13, 24]
    fields:			[7]
    paths:			[22, 23]
  },
  {
    neighbours:			[23, 25, 36]
    fields:			[7, 12]
    paths:			[23, 37, 38]
  },
  {
    neighbours:			[21, 34, 24]
    fields:			[7, 11, 12]
    paths:			[35, 36, 37]
  },
  {
    neighbours:			[18, 29]
    fields:			[8]
    paths:			[24, 25]
  },
  {
    neighbours:			[17, 28, 31]
    fields:			[8, 9, 13]
    paths:			[27, 43, 44]
  },
  {
    neighbours:			[29, 41, 27]
    fields:			[8, 13]
    paths:			[40, 42, 43]
  },
  {
    neighbours:			[26, 28]
    fields:			[8]
    paths:			[24, 40]
  },
  {
    neighbours:			[20, 31, 33]
    fields:			[9, 10, 14]
    paths:			[30, 46, 47]
  },
  {
    neighbours:			[27, 39, 30]
    fields:			[9, 13, 14]
    paths:			[44, 45, 46]
  },
  {
    neighbours:			[22, 33, 35]
    fields:			[10, 11, 15]
    paths:			[33, 49, 50]
  },
  {
    neighbours:			[30, 42, 32]
    fields:			[10, 14, 15]
    paths:			[47, 48, 49]
  },
  {
    neighbours:			[25, 35, 38]
    fields:			[11, 12, 16]
    paths:			[36, 52, 53]
  },
  {
    neighbours:			[32, 44, 34]
    fields:			[11, 15, 16]
    paths:			[50, 51, 52]
  },
  {
    neighbours:			[24, 37]
    fields:			[12]
    paths:			[38, 39]
  },
  {
    neighbours:			[36, 38]
    fields:			[12]
    paths:			[39, 41]
  },
  {
    neighbours:			[34, 46, 37]
    fields:			[12, 16]
    paths:			[53, 54, 41]
  },
  {
    neighbours:			[31, 40, 43]
    fields:			[13, 14, 17]
    paths:			[45, 57, 58]
  },
  {
    neighbours:			[41, 50, 39]
    fields:			[13, 17]
    paths:			[56, 57, 72]
  },
  {
    neighbours:			[28, 40]
    fields:			[13]
    paths:			[42, 72]
  },
  {
    neighbours:			[33, 43, 45]
    fields:			[14, 15, 18]
    paths:			[48, 60, 61]
  },
  {
    neighbours:			[39, 48, 42]
    fields:			[14, 17, 18]
    paths:			[58, 59, 60]
  },
  {
    neighbours:			[35, 45, 47]
    fields:			[15, 16, 19]
    paths:			[51, 63, 64]
  },
  {
    neighbours:			[42, 51, 44]
    fields:			[15, 18, 19]
    paths:			[61, 62, 63]
  },
  {
    neighbours:			[38, 47]
    fields:			[16]
    paths:			[54, 55]
  },
  {
    neighbours:			[44, 53, 46]
    fields:			[16, 19]
    paths:			[55, 64, 65]
  },
  {
    neighbours:			[43, 49, 52]
    fields:			[17, 18]
    paths:			[59, 67, 68]
  },
  {
    neighbours:			[50, 48]
    fields:			[17]
    paths:			[66, 67]
  },
  {
    neighbours:			[40, 49]
    fields:			[17]
    paths:			[56, 66]
  },
  {
    neighbours:			[45, 52, 54]
    fields:			[18, 19]
    paths:			[62, 69, 70]
  },
  {
    neighbours:			[48, 51]
    fields:			[18]
    paths:			[68, 69]
  },
  {
    neighbours:			[47, 54]
    fields:			[19]
    paths:			[65, 71]
  },
  {
    neighbours:			[51, 53]
    fields:			[19]
    paths:			[70, 71]
  },
]

window.settlers.board_defs.paths = [
  null,
  {
    nodes:			[1, 2]
  },
  {
    nodes:			[2, 3]
  },
  {
    nodes:			[1, 6]
  },
  {
    nodes:			[3, 4]
  },
  {
    nodes:			[3, 7]
  },
  {
    nodes:			[7, 8]
  },
  {
    nodes:			[8, 9]
  },
  {
    nodes:			[8, 11]
  },
  {
    nodes:			[11, 12]
  },
  {
    nodes:			[12, 13]
  },
  {
    nodes:			[15, 18]
  },
  {
    nodes:			[15, 6]
  },
  {
    nodes:			[6, 5]
  },
  {
    nodes:			[5, 16]
  },
  {
    nodes:			[5, 4]
  },
  {
    nodes:			[4, 10]
  },
  {
    nodes:			[10, 19]
  },
  {
    nodes:			[10, 9]
  },
  {
    nodes:			[9, 14]
  },
  {
    nodes:			[14, 21]
  },
  {
    nodes:			[14, 13]
  },
  {
    nodes:			[13, 23]
  },
  {
    nodes:			[23, 24]
  },
  {
    nodes:			[26, 29]
  },
  {
    nodes:			[18, 26]
  },
  {
    nodes:			[18, 17]
  },
  {
    nodes:			[17, 27]
  },
  {
    nodes:			[17, 16]
  },
  {
    nodes:			[16, 20]
  },
  {
    nodes:			[20, 30]
  },
  {
    nodes:			[20, 19]
  },
  {
    nodes:			[19, 22]
  },
  {
    nodes:			[22, 32]
  },
  {
    nodes:			[22, 21]
  },
  {
    nodes:			[21, 25]
  },
  {
    nodes:			[25, 34]
  },
  {
    nodes:			[25, 24]
  },
  {
    nodes:			[24, 36]
  },
  {
    nodes:			[36, 37]
  },
  {
    nodes:			[29, 28]
  },
  {
    nodes:			[37, 38]
  },
  {
    nodes:			[28, 41]
  },
  {
    nodes:			[28, 27]
  },
  {
    nodes:			[27, 31]
  },
  {
    nodes:			[31, 39]
  },
  {
    nodes:			[31, 30]
  },
  {
    nodes:			[30, 33]
  },
  {
    nodes:			[33, 42]
  },
  {
    nodes:			[33, 32]
  },
  {
    nodes:			[32, 35]
  },
  {
    nodes:			[35, 44]
  },
  {
    nodes:			[35, 34]
  },
  {
    nodes:			[34, 38]
  },
  {
    nodes:			[38, 46]
  },
  {
    nodes:			[46, 47]
  },
  {
    nodes:			[40, 50]
  },
  {
    nodes:			[40, 39]
  },
  {
    nodes:			[39, 43]
  },
  {
    nodes:			[43, 48]
  },
  {
    nodes:			[43, 42]
  },
  {
    nodes:			[42, 45]
  },
  {
    nodes:			[45, 51]
  },
  {
    nodes:			[45, 44]
  },
  {
    nodes:			[44, 47]
  },
  {
    nodes:			[47, 53]
  },
  {
    nodes:			[50, 49]
  },
  {
    nodes:			[48, 49]
  },
  {
    nodes:			[48, 52]
  },
  {
    nodes:			[52, 51]
  },
  {
    nodes:			[51, 54]
  },
  {
    nodes:			[54, 53]
  },
  {
    nodes:			[40, 41]
  },
]

