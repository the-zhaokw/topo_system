// 重现频率中英文映射
const frequencyMap = {
  always: '必然复现',
  often: '经常复现',
  occasionally: '偶尔复现',
  never: '无法复现'
}

export function formatFrequency(value) {
  if (!value) return '-'
  return frequencyMap[value] || value
}
