export interface MaterialReport {
  totalMaterials: number;
  totalValue: number;
  lowStockCount: number;
  outOfStockCount: number;
  categoryDistribution: CategoryDist[];
  warehouseDistribution: WarehouseDist[];
  monthlyUsage: MonthlyUsage[];
  topMaterials: MaterialUsage[];
}

export interface CategoryDist {
  categoryName: string;
  count: number;
  value: number;
}

export interface WarehouseDist {
  warehouseName: string;
  count: number;
  value: number;
}

export interface MonthlyUsage {
  month: string;
  usageCount: number;
  usageValue: number;
}

export interface MaterialUsage {
  materialName: string;
  usageCount: number;
  usageValue: number;
}

export interface MaterialCategory {
  id: number;
  categoryName: string;
  parentId?: number;
  materialCount: number;
  description?: string;
}

export interface MaterialRelationship {
  id: number;
  parentMaterial: string;
  childMaterial: string;
  relationshipType: '组成' | '替代' | '互斥' | '可选';
  quantity?: number;
}

export interface SerialNumber {
  id: number;
  serialNo: string;
  materialName: string;
  warehouse: string;
  location: string;
  status: '库存' | '使用中' | '维修中' | '已报废';
  purchaseDate: string;
  warrantyExpiry?: string;
}

export interface Warehouse {
  id: number;
  warehouseName: string;
  address: string;
  manager: string;
  capacity: number;
  currentStock: number;
  utilizationRate: number;
}

export interface Location {
  id: number;
  locationCode: string;
  warehouseName: string;
  zone: string;
  shelf: string;
  capacity: number;
  currentStock: number;
}

export interface InventoryItem {
  id: number;
  materialName: string;
  materialNo: string;
  warehouse: string;
  location: string;
  quantity: number;
  unit: string;
  minStock: number;
  maxStock: number;
  status: '正常' | '库存不足' | '库存过剩';
}
