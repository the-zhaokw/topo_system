/**
 * 物料管理系统API服务
 */

import api from './api';

class MaterialsService {
  // ==================== 物料分类管理 ====================
  
  /**
   * 获取物料分类列表
   */
  async getCategories() {
    const response = await api.get('/materials/categories');
    return response;
  }

  /**
   * 获取单个物料分类详情
   */
  async getCategory(categoryId) {
    const response = await api.get(`/materials/categories/${categoryId}`);
    return response;
  }

  /**
   * 创建物料分类
   */
  async createCategory(categoryData) {
    const response = await api.post('/materials/categories', categoryData);
    return response;
  }

  /**
   * 更新物料分类
   */
  async updateCategory(categoryId, categoryData) {
    const response = await api.put(`/materials/categories/${categoryId}`, categoryData);
    return response;
  }

  /**
   * 删除物料分类
   */
  async deleteCategory(categoryId) {
    const response = await api.delete(`/materials/categories/${categoryId}`);
    return response;
  }

  // ==================== 物料主数据管理 ====================

  /**
   * 获取物料列表
   */
  async getMaterials(params = {}) {
    const response = await api.get('/materials/', { params });
    return response;
  }

  /**
   * 获取单个物料详情
   */
  async getMaterial(materialId) {
    const response = await api.get(`/materials/${materialId}`);
    return response;
  }

  /**
   * 创建物料
   */
  async createMaterial(materialData) {
    const response = await api.post('/materials/', materialData);
    return response;
  }

  /**
   * 更新物料
   */
  async updateMaterial(materialId, materialData) {
    const response = await api.put(`/materials/${materialId}`, materialData);
    return response;
  }

  /**
   * 删除物料
   */
  async deleteMaterial(materialId) {
    const response = await api.delete(`/materials/${materialId}`);
    return response;
  }

  // ==================== 仓库管理 ====================

  /**
   * 获取仓库列表
   */
  async getWarehouses() {
    const response = await api.get('/materials/warehouses');
    return response;
  }

  /**
   * 获取单个仓库详情
   */
  async getWarehouse(warehouseId) {
    const response = await api.get(`/materials/warehouses/${warehouseId}`);
    return response;
  }

  /**
   * 创建仓库
   */
  async createWarehouse(warehouseData) {
    const response = await api.post('/materials/warehouses', warehouseData);
    return response;
  }

  /**
   * 更新仓库
   */
  async updateWarehouse(warehouseId, warehouseData) {
    const response = await api.put(`/materials/warehouses/${warehouseId}`, warehouseData);
    return response;
  }

  /**
   * 删除仓库
   */
  async deleteWarehouse(warehouseId) {
    const response = await api.delete(`/materials/warehouses/${warehouseId}`);
    return response;
  }

  // ==================== 库位管理 ====================

  /**
   * 获取库位列表
   */
  async getLocations(warehouseId = null) {
    const params = warehouseId ? { warehouse_id: warehouseId } : {};
    const response = await api.get('/materials/locations', { params });
    return response;
  }

  /**
   * 获取单个库位详情
   */
  async getLocation(locationId) {
    const response = await api.get(`/materials/locations/${locationId}`);
    return response;
  }

  /**
   * 创建库位
   */
  async createLocation(locationData) {
    const response = await api.post('/materials/locations', locationData);
    return response;
  }

  /**
   * 更新库位
   */
  async updateLocation(locationId, locationData) {
    const response = await api.put(`/materials/locations/${locationId}`, locationData);
    return response;
  }

  /**
   * 删除库位
   */
  async deleteLocation(locationId) {
    const response = await api.delete(`/materials/locations/${locationId}`);
    return response;
  }

  // ==================== 库存管理 ====================

  /**
   * 获取库存列表
   */
  async getInventory(params = {}) {
    const response = await api.get('/materials/inventory', { params });
    return response;
  }

  /**
   * 获取库存统计
   */
  async getInventoryStats() {
    const response = await api.get('/materials/inventory/stats');
    return response;
  }

  // ==================== 库存交易管理 ====================

  /**
   * 获取库存交易列表
   */
  async getTransactions(params = {}) {
    const response = await api.get('/materials/transactions', { params });
    return response;
  }

  /**
   * 获取单个交易详情
   */
  async getTransaction(transactionId) {
    const response = await api.get(`/materials/transactions/${transactionId}`);
    return response;
  }

  /**
   * 创建库存交易
   */
  async createTransaction(transactionData) {
    const response = await api.post('/materials/transactions', transactionData);
    return response;
  }

  // ==================== 序列号管理 ====================

  /**
   * 获取序列号列表
   */
  async getSerialNumbers(params = {}) {
    const response = await api.get('/materials/serial-numbers', { params });
    return response;
  }

  /**
   * 获取单个序列号详情
   */
  async getSerialNumber(serialNumberId) {
    const response = await api.get(`/materials/serial-numbers/${serialNumberId}`);
    return response;
  }

  /**
   * 创建序列号
   */
  async createSerialNumber(serialNumberData) {
    const response = await api.post('/materials/serial-numbers', serialNumberData);
    return response;
  }

  /**
   * 更新序列号
   */
  async updateSerialNumber(serialNumberId, serialNumberData) {
    const response = await api.put(`/materials/serial-numbers/${serialNumberId}`, serialNumberData);
    return response;
  }

  // ==================== 物料关系管理 ====================

  /**
   * 获取物料关系列表
   */
  async getRelationships(params = {}) {
    const response = await api.get('/materials/relationships', { params });
    return response;
  }

  /**
   * 创建物料关系
   */
  async createRelationship(relationshipData) {
    const response = await api.post('/materials/relationships', relationshipData);
    return response;
  }

  /**
   * 删除物料关系
   */
  async deleteRelationship(relationshipId) {
    const response = await api.delete(`/materials/relationships/${relationshipId}`);
    return response;
  }

  // ==================== 物料统计报表 (F-007-05) ====================

  /**
   * 获取库存总价值统计
   */
  async getInventoryValue(params = {}) {
    const response = await api.get('/materials/reports/inventory-value', { params });
    return response;
  }

  /**
   * 获取出入库频率Top物料
   */
  async getTopMaterials(params = {}) {
    const response = await api.get('/materials/reports/top-materials', { params });
    return response;
  }

  /**
   * 获取库存汇总报表
   */
  async getInventorySummary(params = {}) {
    const response = await api.get('/materials/reports/inventory-summary', { params });
    return response;
  }

  /**
   * 获取物料流水报表
   */
  async getTransactionReport(params = {}) {
    const response = await api.get('/materials/reports/material-flow', { params });
    return response;
  }

  /**
   * 获取库存预警信息
   */
  async getInventoryAlerts(params = {}) {
    const response = await api.get('/materials/alerts', { params });
    return response;
  }

  /**
   * 获取物料预警报表
   */
  async getMaterialAlerts(params = {}) {
    const response = await api.get('/materials/reports/material-alerts', { params });
    return response;
  }

  /**
   * 获取物料周转率统计
   */
  async getMaterialTurnover(params = {}) {
    const response = await api.get('/materials/reports/material-turnover', { params });
    return response;
  }
}

export default new MaterialsService();