import { MaterialReport, MaterialCategory, SerialNumber, Warehouse, Location, InventoryItem } from '../types/material';

export const mockMaterialReport: MaterialReport = {
  totalMaterials: 1256,
  totalValue: 2580000,
  lowStockCount: 23,
  outOfStockCount: 5,
  categoryDistribution: [
    { categoryName: '电子元器件', count: 456, value: 980000 },
    { categoryName: '结构件', count: 321, value: 650000 },
    { categoryName: '线缆连接器', count: 234, value: 420000 },
    { categoryName: '光学器件', count: 145, value: 380000 },
    { categoryName: '其他材料', count: 100, value: 150000 }
  ],
  warehouseDistribution: [
    { warehouseName: 'A仓库', count: 678, value: 1450000 },
    { warehouseName: 'B仓库', count: 389, value: 780000 },
    { warehouseName: 'C仓库', count: 189, value: 350000 }
  ],
  monthlyUsage: [
    { month: '2026-01', usageCount: 234, usageValue: 156000 },
    { month: '2026-02', usageCount: 198, usageValue: 142000 },
    { month: '2026-03', usageCount: 267, usageValue: 189000 },
    { month: '2026-04', usageCount: 245, usageValue: 168000 },
    { month: '2026-05', usageCount: 178, usageValue: 125000 }
  ],
  topMaterials: [
    { materialName: 'FPGA芯片', usageCount: 156, usageValue: 234000 },
    { materialName: '高速连接器', usageCount: 234, usageValue: 187200 },
    { materialName: 'PCB板', usageCount: 189, usageValue: 151200 }
  ]
};

export const mockMaterialCategory: MaterialCategory[] = [
  { id: 1, categoryName: '电子元器件', materialCount: 456, description: '各类电子元器件' },
  { id: 2, categoryName: '结构件', materialCount: 321, description: '机械结构件' },
  { id: 3, categoryName: '线缆连接器', materialCount: 234, description: '线缆和连接器' },
  { id: 4, categoryName: '光学器件', materialCount: 145, description: '光学相关器件' }
];

export const mockSerialNumber: SerialNumber[] = [
  {
    id: 1,
    serialNo: 'SN202605010001',
    materialName: 'FPGA芯片',
    warehouse: 'A仓库',
    location: 'A-01-02-03',
    status: '库存',
    purchaseDate: '2026-04-15',
    warrantyExpiry: '2028-04-15'
  },
  {
    id: 2,
    serialNo: 'SN202605010002',
    materialName: '高速连接器',
    warehouse: 'A仓库',
    location: 'A-01-02-04',
    status: '使用中',
    purchaseDate: '2026-03-20'
  }
];

export const mockWarehouse: Warehouse[] = [
  {
    id: 1,
    warehouseName: 'A仓库',
    address: '深圳市南山区科技园',
    manager: '张主管',
    capacity: 1000,
    currentStock: 678,
    utilizationRate: 67.8
  },
  {
    id: 2,
    warehouseName: 'B仓库',
    address: '深圳市宝安区',
    manager: '李主管',
    capacity: 800,
    currentStock: 389,
    utilizationRate: 48.6
  }
];

export const mockLocation: Location[] = [
  {
    id: 1,
    locationCode: 'A-01-02-03',
    warehouseName: 'A仓库',
    zone: 'A区',
    shelf: '01-02',
    capacity: 100,
    currentStock: 67
  },
  {
    id: 2,
    locationCode: 'A-01-02-04',
    warehouseName: 'A仓库',
    zone: 'A区',
    shelf: '01-02',
    capacity: 100,
    currentStock: 45
  }
];

export const mockInventoryItem: InventoryItem[] = [
  {
    id: 1,
    materialName: 'FPGA芯片',
    materialNo: 'MAT-001',
    warehouse: 'A仓库',
    location: 'A-01-02-03',
    quantity: 150,
    unit: '个',
    minStock: 50,
    maxStock: 500,
    status: '正常'
  },
  {
    id: 2,
    materialName: '高速连接器',
    materialNo: 'MAT-002',
    warehouse: 'A仓库',
    location: 'A-01-02-04',
    quantity: 30,
    unit: '个',
    minStock: 50,
    maxStock: 300,
    status: '库存不足'
  }
];
