<template>
  <div class="requirement-doc-detail" v-loading="loading">
    <div v-if="document">
      <!-- 头部导航 -->
      <div class="detail-header">
        <div class="header-left">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="doc-info">
            <h2>{{ document.name }}</h2>
            <div class="doc-tags">
              <el-tag :type="getStatusType(document.status)" size="small">
                {{ getStatusText(document.status) }}
              </el-tag>
              <el-tag type="info" size="small">v{{ document.version }}</el-tag>
              <el-tag type="info" size="small" v-if="document.doc_type === 'functional'">功能需求</el-tag>
              <el-tag type="warning" size="small" v-else>非功能需求</el-tag>
            </div>
          </div>
        </div>
        <div class="header-right">
          <el-button @click="goToTraceMatrix">
            <el-icon><Connection /></el-icon>
            跟踪矩阵
          </el-button>
          <el-button @click="goToImpactAnalysis" v-if="selectedItem">
            <el-icon><Warning /></el-icon>
            影响分析
          </el-button>
          <el-dropdown @command="handleExport" trigger="click">
            <el-button>
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="markdown">导出为 Markdown</el-dropdown-item>
                <el-dropdown-item command="html">导出为 HTML</el-dropdown-item>
                <el-dropdown-item command="json">导出为 JSON</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button @click="showVersionHistory = true">
            <el-icon><Clock /></el-icon>
            版本历史
          </el-button>
          <el-button type="warning" @click="showVersionCompare = true" v-if="canManage">
            <el-icon><Connection /></el-icon>
            版本对比
          </el-button>
          <el-button type="primary" @click="showEditDialog = true" v-if="canEdit">
            <el-icon><Edit /></el-icon>
            编辑文档
          </el-button>
          <el-button type="success" @click="showReviewDialog = true" v-if="canManage">
            <el-icon><Select /></el-icon>
            发起评审
          </el-button>
        </div>
      </div>

      <!-- 文档描述 -->
      <el-card class="description-card" v-if="document.description">
        <template #header>
          <span>文档描述</span>
        </template>
        <div class="description-content">{{ document.description }}</div>
      </el-card>

      <!-- 需求条目列表 -->
      <el-card class="items-card">
        <template #header>
          <div class="items-header">
            <span>需求条目 ({{ items.length }})</span>
            <div class="header-actions">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索需求"
                clearable
                style="width: 200px; margin-right: 12px;"
              />
              <el-button type="primary" @click="openCreateItemDialog" v-if="canEdit">
                <el-icon><Plus /></el-icon>
                新建条目
              </el-button>
            </div>
          </div>
        </template>

        <el-empty v-if="filteredItems.length === 0" description="暂无需求条目" />
        
        <div v-else class="items-list">
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="item-row"
            :class="{ 'expanded': expandedItems.includes(item.id) }"
            :data-item-id="item.id"
          >
            <div class="item-summary" @click="toggleExpand(item.id)">
              <div class="item-left">
                <el-icon class="expand-icon"><ArrowRight /></el-icon>
                <span class="item-identifier">{{ item.identifier }}</span>
                <span class="item-title">{{ item.title }}</span>
                <el-tag :type="getItemStatusType(item.status)" size="small">
                  {{ getItemStatusText(item.status) }}
                </el-tag>
                <el-tag 
                  :type="getPriorityType(item.priority)" 
                  size="small"
                  v-if="item.priority"
                >
                  {{ getPriorityText(item.priority) }}
                </el-tag>
              </div>
              <div class="item-right">
                <span class="item-owner" v-if="item.owner_name">
                  <el-icon><User /></el-icon>
                  {{ item.owner_name }}
                </span>
                <span class="item-comments" v-if="item.comment_count">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ item.comment_count }}
                </span>
                <div class="item-actions">
                  <el-tooltip content="编辑" placement="top">
                    <el-button type="primary" link size="small" @click.stop="handleItemCommand('edit', item)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="变更状态" placement="top">
                    <el-button type="warning" link size="small" @click.stop="handleItemCommand('status', item)">
                      <el-icon><View /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="复制条目" placement="top">
                    <el-button type="info" link size="small" @click.stop="handleItemCommand('copy', item)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="移动条目" placement="top">
                    <el-button type="info" link size="small" @click.stop="handleItemCommand('move', item)">
                      <el-icon><Rank /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="变更历史" placement="top">
                    <el-button type="info" link size="small" @click.stop="handleItemCommand('history', item)">
                      <el-icon><Timer /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="影响分析" placement="top">
                    <el-button type="info" link size="small" @click.stop="handleItemCommand('impact', item)">
                      <el-icon><Warning /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="评审" placement="top">
                    <el-button type="success" link size="small" @click.stop="handleItemCommand('review', item)">
                      <el-icon><Share /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                    <el-button type="danger" link size="small" @click.stop="handleItemCommand('delete', item)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </div>
            
            <!-- 展开详情 -->
            <div v-if="expandedItems.includes(item.id)" class="item-detail">
              <el-divider />
              <div class="detail-section">
                <h4>需求描述</h4>
                <div class="detail-content" v-text="item.description || '暂无描述'"></div>
              </div>
              
              <div class="detail-grid">
                <div class="detail-item">
                  <label>模块:</label>
                  <span>{{ item.module || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>负责人:</label>
                  <span>{{ item.owner_name || '未分配' }}</span>
                </div>
                <div class="detail-item">
                  <label>提出人:</label>
                  <span>{{ item.creator_name }}</span>
                </div>
                <div class="detail-item">
                  <label>计划版本:</label>
                  <span>{{ item.planned_version || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>实际版本:</label>
                  <span>{{ item.actual_version || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>创建时间:</label>
                  <span>{{ formatDate(item.created_at) }}</span>
                </div>
              </div>

              <!-- 关联链接展示 -->
              <div class="detail-section" v-if="item.links && item.links.length > 0">
                <h4>关联链接</h4>
                <div class="links-list">
                  <div v-for="link in item.links" :key="link.id" class="link-item">
                    <el-tag size="small" :type="getLinkTypeTag(link.link_type)">
                      {{ getLinkTypeText(link.link_type) }}
                    </el-tag>
                    <span class="link-target">{{ link.target_identifier || link.target_url }}</span>
                  </div>
                </div>
              </div>

              <!-- 附件展示 -->
              <div class="detail-section" v-if="item.attachments && item.attachments.length > 0">
                <h4>附件</h4>
                <AttachmentList
                  :attachments="item.attachments"
                  :editable="false"
                  :entity-type="'requirement_item'"
                  :entity-id="item.id"
                />
              </div>
              
              <!-- 评论区域 -->
              <div class="comments-section">
                <h4>评论</h4>
                <RequirementComments 
                  :target-type="'item'"
                  :target-id="item.id"
                />
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 编辑文档对话框 -->
      <el-dialog v-model="showEditDialog" title="编辑需求文档" width="600px">
        <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
          <el-form-item label="文档名称" prop="name">
            <el-input v-model="editForm.name" />
          </el-form-item>
          <el-form-item label="文档类型" prop="docType">
            <el-radio-group v-model="editForm.docType">
              <el-radio label="functional">功能需求</el-radio>
              <el-radio label="non_functional">非功能需求</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="文档描述" prop="description">
            <el-input 
              v-model="editForm.description" 
              type="textarea" 
              :rows="4"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdate" :loading="updating">
            保存
          </el-button>
        </template>
      </el-dialog>

      <!-- 新建条目对话框 -->
      <el-dialog v-model="showCreateItemDialog" title="新建需求条目" width="800px" class="item-dialog">
        <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="100px">
          <el-form-item label="需求标识" prop="identifier">
            <el-input v-model="itemForm.identifier" placeholder="如 REQ-001" />
          </el-form-item>
          <el-form-item label="需求标题" prop="title">
            <el-input v-model="itemForm.title" placeholder="请输入需求标题" />
          </el-form-item>
          <el-form-item label="详细描述" prop="description">
            <RichTextEditor v-model="itemForm.description" placeholder="请输入详细描述..." :editorType="'simple'" :rows="6" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="优先级" prop="priority">
                <el-radio-group v-model="itemForm.priority">
                  <el-radio :label="3">高</el-radio>
                  <el-radio :label="2">中</el-radio>
                  <el-radio :label="1">低</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模块" prop="module">
                <el-select v-model="itemForm.module" filterable allow-create clearable placeholder="选择或输入模块" style="width: 100%;">
                  <el-option v-for="mod in moduleOptions" :key="mod" :label="mod" :value="mod" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="负责人" prop="ownerId">
            <UserSelector v-model="itemForm.ownerId" :projectId="projectId" :multiple="false" placeholder="选择负责人" />
          </el-form-item>
          <el-form-item label="计划版本" prop="plannedVersion">
            <el-input v-model="itemForm.plannedVersion" placeholder="如：v1.0.0" />
          </el-form-item>

          <el-divider content-position="left">关联链接</el-divider>
          <div class="links-editor">
            <div v-for="(link, index) in itemForm.links" :key="index" class="link-row">
              <el-select v-model="link.linkType" style="width: 120px; margin-right: 8px;">
                <el-option label="实现" value="implements" />
                <el-option label="验证" value="verifies" />
                <el-option label="影响" value="affects" />
                <el-option label="相关" value="related" />
              </el-select>
              <el-select v-model="link.targetType" style="width: 120px; margin-right: 8px;">
                <el-option label="任务" value="task" />
                <el-option label="缺陷" value="bug" />
                <el-option label="测试用例" value="test_case" />
              </el-select>
              <el-input-number v-model="link.targetId" :min="1" style="width: 150px; margin-right: 8px;" />
              <el-button type="danger" link @click="removeLink(index)"><el-icon><Delete /></el-icon></el-button>
            </div>
            <el-button type="primary" link @click="addLink"><el-icon><Plus /></el-icon> 添加链接</el-button>
          </div>

          <el-divider content-position="left">附件</el-divider>
          <AttachmentList
            ref="createAttachmentRef"
            :editable="true"
            :entity-type="'requirement_item'"
            :entity-id="null"
            @upload="handleAttachmentUpload"
          />
        </el-form>
        <template #footer>
          <el-button @click="showCreateItemDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateItem" :loading="creatingItem">
            创建
          </el-button>
        </template>
      </el-dialog>

      <!-- 编辑条目对话框 -->
      <el-dialog v-model="showEditItemDialog" title="编辑需求条目" width="800px" class="item-dialog">
        <el-form :model="editItemForm" :rules="itemRules" ref="editItemFormRef" label-width="100px">
          <el-form-item label="需求标题" prop="title">
            <el-input v-model="editItemForm.title" />
          </el-form-item>
          <el-form-item label="详细描述" prop="description">
            <RichTextEditor v-model="editItemForm.description" placeholder="请输入详细描述..." :editorType="'simple'" :rows="6" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="优先级" prop="priority">
                <el-radio-group v-model="editItemForm.priority">
                  <el-radio :label="3">高</el-radio>
                  <el-radio :label="2">中</el-radio>
                  <el-radio :label="1">低</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="editItemForm.status" style="width: 100%;">
                  <el-option label="待评审" value="pending_review" />
                  <el-option label="已评审" value="reviewed" />
                  <el-option label="已批准" value="approved" />
                  <el-option label="开发中" value="in_progress" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已验证" value="verified" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="负责人" prop="ownerId">
                <UserSelector v-model="editItemForm.ownerId" :projectId="projectId" :multiple="false" placeholder="选择负责人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="模块" prop="module">
                <el-select v-model="editItemForm.module" filterable allow-create clearable placeholder="选择或输入模块" style="width: 100%;">
                  <el-option v-for="mod in moduleOptions" :key="mod" :label="mod" :value="mod" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="计划版本" prop="plannedVersion">
                <el-input v-model="editItemForm.plannedVersion" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="实际版本" prop="actualVersion">
                <el-input v-model="editItemForm.actualVersion" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">关联链接</el-divider>
          <div class="links-editor">
            <div v-for="(link, index) in editItemForm.links" :key="index" class="link-row">
              <el-select v-model="link.linkType" style="width: 120px; margin-right: 8px;">
                <el-option label="实现" value="implements" />
                <el-option label="验证" value="verifies" />
                <el-option label="影响" value="affects" />
                <el-option label="相关" value="related" />
              </el-select>
              <el-select v-model="link.targetType" style="width: 120px; margin-right: 8px;">
                <el-option label="任务" value="task" />
                <el-option label="缺陷" value="bug" />
                <el-option label="测试用例" value="test_case" />
              </el-select>
              <el-input-number v-model="link.targetId" :min="1" style="width: 150px; margin-right: 8px;" />
              <el-button type="danger" link @click="removeEditLink(index)"><el-icon><Delete /></el-icon></el-button>
            </div>
            <el-button type="primary" link @click="addEditLink"><el-icon><Plus /></el-icon> 添加链接</el-button>
          </div>

          <el-divider content-position="left">附件</el-divider>
          <AttachmentList
            ref="editAttachmentRef"
            :attachments="editItemForm.attachments || []"
            :editable="true"
            :entity-type="'requirement_item'"
            :entity-id="editItemForm.id"
            @upload="handleAttachmentUpload"
          />
        </el-form>
        <template #footer>
          <el-button @click="showEditItemDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateItem" :loading="updatingItem">
            保存
          </el-button>
        </template>
      </el-dialog>

      <!-- 版本历史对话框 -->
      <el-dialog v-model="showVersionHistory" title="版本历史" width="700px">
        <el-timeline>
          <el-timeline-item
            v-for="version in versions"
            :key="version.id"
            :timestamp="formatDate(version.created_at)"
            placement="top"
          >
            <el-card>
              <h4>版本 {{ version.version }}</h4>
              <p v-if="version.change_summary">{{ version.change_summary }}</p>
              <p class="version-creator">创建者: {{ version.creator_name }}</p>
              <el-button type="primary" link size="small" @click="handleRollback(version.version)" v-if="canManage && version.version !== document.version">
                回滚到此版本
              </el-button>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <template #footer>
          <el-button @click="showVersionHistory = false">关闭</el-button>
          <el-button type="primary" @click="handleCreateVersion" v-if="canEdit">
            创建新版本
          </el-button>
        </template>
      </el-dialog>

      <!-- 版本对比对话框 -->
      <el-dialog v-model="showVersionCompare" title="版本对比" width="900px">
        <el-form :inline="true">
          <el-form-item label="版本1">
            <el-select v-model="compareVersion1" placeholder="选择版本" style="width: 150px;">
              <el-option v-for="v in versions" :key="v.id" :label="`v${v.version}`" :value="v.version" />
            </el-select>
          </el-form-item>
          <el-form-item label="版本2">
            <el-select v-model="compareVersion2" placeholder="选择版本" style="width: 150px;">
              <el-option v-for="v in versions" :key="v.id" :label="`v${v.version}`" :value="v.version" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchVersionDiff">对比</el-button>
          </el-form-item>
        </el-form>
        <div v-if="versionDiff" class="diff-result">
          <el-alert v-if="versionDiff.document?.name_changed" title="文档名称已修改" type="warning" :closable="false" />
          <el-alert v-if="versionDiff.document?.description_changed" title="文档描述已修改" type="warning" :closable="false" />
          <el-alert v-if="versionDiff.document?.status_changed" title="文档状态已修改" type="warning" :closable="false" />
          <div v-if="versionDiff.items_added?.length" class="diff-section">
            <h4>新增的需求条目:</h4>
            <div v-for="item in versionDiff.items_added" :key="item.identifier" class="diff-item diff-added">
              {{ item.identifier }} - {{ item.title }}
            </div>
          </div>
          <div v-if="versionDiff.items_removed?.length" class="diff-section">
            <h4>删除的需求条目:</h4>
            <div v-for="item in versionDiff.items_removed" :key="item.identifier" class="diff-item diff-removed">
              {{ item.identifier }} - {{ item.title }}
            </div>
          </div>
          <div v-if="versionDiff.items_modified?.length" class="diff-section">
            <h4>修改的需求条目:</h4>
            <div v-for="item in versionDiff.items_modified" :key="item.identifier" class="diff-item diff-modified">
              {{ item.identifier }} - {{ item.title }}
            </div>
          </div>
        </div>
      </el-dialog>

      <!-- 发起评审对话框 -->
      <el-dialog v-model="showReviewDialog" title="发起评审" width="550px">
        <el-form :model="reviewForm" ref="reviewFormRef" label-width="100px">
          <el-form-item label="评审范围">
            <el-radio-group v-model="reviewForm.scope">
              <el-radio label="all">整个文档</el-radio>
              <el-radio label="items">部分条目</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="评审人员">
            <UserSelector v-model="reviewForm.reviewers" :projectId="projectId" :multiple="true" placeholder="选择评审人员" />
          </el-form-item>
          <el-form-item label="截止时间">
            <el-date-picker v-model="reviewForm.deadline" type="datetime" placeholder="选择截止时间" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="补充说明">
            <el-input v-model="reviewForm.comment" type="textarea" :rows="3" placeholder="请输入补充说明" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showReviewDialog = false">取消</el-button>
          <el-button type="primary" @click="handleInitiateReview" :loading="submittingReview">
            发起评审
          </el-button>
        </template>
      </el-dialog>

      <!-- 复制/移动条目对话框 -->
      <el-dialog v-model="showCopyMoveDialog" :title="copyMoveAction === 'copy' ? '复制需求条目' : '移动需求条目'" width="500px">
        <el-form :model="copyMoveForm" ref="copyMoveFormRef" label-width="100px">
          <el-form-item label="目标文档">
            <el-select v-model="copyMoveForm.targetDocId" placeholder="选择目标文档" style="width: 100%;">
              <el-option v-for="doc in projectDocuments" :key="doc.id" :label="doc.name" :value="doc.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showCopyMoveDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCopyMove" :loading="submittingCopyMove">
            确认
          </el-button>
        </template>
      </el-dialog>

      <!-- 条目历史对话框 -->
      <el-dialog v-model="showHistoryDialog" title="变更历史" width="700px">
        <el-timeline>
          <el-timeline-item v-for="h in itemHistory" :key="h.id" :timestamp="formatDate(h.created_at)" placement="top">
            <el-card>
              <p><strong>{{ h.field }}</strong>: {{ h.old_value }} → {{ h.new_value }}</p>
              <p class="version-creator">操作人: {{ h.operator_name }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-if="itemHistory.length === 0" description="暂无变更历史" />
      </el-dialog>

      <!-- 影响分析对话框 -->
      <el-dialog v-model="showImpactDialog" title="变更影响分析" width="700px">
        <div v-if="impactAnalysis">
          <el-divider content-position="left">{{ impactAnalysis.requirement?.identifier }} - {{ impactAnalysis.requirement?.title }}</el-divider>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="关联任务" :value="impactAnalysis.impacted_items?.tasks?.length || 0" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="关联缺陷" :value="impactAnalysis.impacted_items?.bugs?.length || 0" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="关联测试用例" :value="impactAnalysis.impacted_items?.test_cases?.length || 0" />
            </el-col>
          </el-row>
        </div>
      </el-dialog>

      <!-- 条目评审对话框 -->
      <el-dialog v-model="showItemReviewDialog" title="评审需求条目" width="500px">
        <el-form :model="itemReviewForm" ref="itemReviewFormRef" label-width="100px">
          <el-form-item label="评审结论">
            <el-radio-group v-model="itemReviewForm.conclusion">
              <el-radio label="approved">通过</el-radio>
              <el-radio label="needs_modification">需要修改</el-radio>
              <el-radio label="rejected">拒绝</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="评审意见">
            <el-input v-model="itemReviewForm.comment" type="textarea" :rows="4" placeholder="请输入评审意见" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showItemReviewDialog = false">取消</el-button>
          <el-button type="primary" @click="handleItemReview" :loading="submittingItemReview">
            提交评审
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Edit, Plus, ArrowRight, User,
  ChatDotRound, More, Clock, Connection, Warning, Download, Select,
  Delete, CopyDocument, Rank, Timer, Share, View
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'
import RequirementComments from '@/components/RequirementComments.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import AttachmentList from '@/components/common/AttachmentList.vue'
import UserSelector from '@/components/common/UserSelector.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const document = ref(null)
const items = ref([])
const versions = ref([])
const projectMembers = ref([])
const projectDocuments = ref([])
const expandedItems = ref([])
const selectedItem = ref(null)
const searchKeyword = ref('')

const showEditDialog = ref(false)
const showCreateItemDialog = ref(false)
const showEditItemDialog = ref(false)
const showVersionHistory = ref(false)
const showVersionCompare = ref(false)
const showReviewDialog = ref(false)
const showCopyMoveDialog = ref(false)
const showHistoryDialog = ref(false)
const showImpactDialog = ref(false)
const showItemReviewDialog = ref(false)

const updating = ref(false)
const creatingItem = ref(false)
const updatingItem = ref(false)
const submittingReview = ref(false)
const submittingCopyMove = ref(false)
const submittingItemReview = ref(false)

const compareVersion1 = ref(null)
const compareVersion2 = ref(null)
const versionDiff = ref(null)

const createAttachmentRef = ref(null)
const editAttachmentRef = ref(null)

const reviewFormRef = ref(null)
const reviewForm = ref({
  reviewers: [],
  deadline: null,
  reviewType: 'document',
  scope: 'all',
  comment: ''
})

const copyMoveFormRef = ref(null)
const copyMoveForm = ref({
  targetDocId: null
})
const copyMoveAction = ref('copy')

const itemHistory = ref([])
const impactAnalysis = ref(null)

const itemReviewFormRef = ref(null)
const itemReviewForm = ref({
  conclusion: 'approved',
  comment: ''
})

const editFormRef = ref(null)
const itemFormRef = ref(null)
const editItemFormRef = ref(null)

const moduleOptions = ref(['用户模块', '订单模块', '支付模块', '商品模块', '权限模块', '通知模块'])

const editForm = ref({
  name: '',
  docType: 'functional',
  description: ''
})

const itemForm = ref({
  identifier: '',
  title: '',
  description: '',
  priority: 2,
  module: '',
  ownerId: null,
  plannedVersion: '',
  links: [],
  attachments: []
})

const editItemForm = ref({
  id: null,
  title: '',
  description: '',
  priority: 2,
  status: 'pending_review',
  ownerId: null,
  module: '',
  plannedVersion: '',
  actualVersion: '',
  links: [],
  attachments: []
})

const editRules = {
  name: [
    { required: true, message: '请输入文档名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ]
}

const itemRules = {
  title: [
    { required: true, message: '请输入需求标题', trigger: 'blur' },
    { min: 2, max: 500, message: '长度在 2 到 500 个字符', trigger: 'blur' }
  ]
}

const docId = computed(() => route.params.docId || route.params.id)
const projectId = computed(() => route.params.projectId)

const canEdit = computed(() => {
  const user = userStore.currentUser
  if (!user || !document.value) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' ||
         position?.includes('经理') ||
         position === '项目经理' ||
         position === '测试工程师' ||
         position === '软件工程师' ||
         document.value.created_by === user.id
})

const canApprove = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' || position?.includes('经理') || position === '项目经理'
})

const canManage = computed(() => {
  const user = userStore.currentUser
  if (!user) return false
  if (user.is_super_admin) return true
  const position = user.position
  return position === '管理员' || position?.includes('经理') || position === '项目经理'
})

const filteredItems = computed(() => {
  if (!searchKeyword.value) return items.value
  const keyword = searchKeyword.value.toLowerCase()
  return items.value.filter(item =>
    item.title.toLowerCase().includes(keyword) ||
    item.identifier.toLowerCase().includes(keyword) ||
    (item.description && item.description.toLowerCase().includes(keyword))
  )
})

const openCreateItemDialog = () => {
  itemForm.value = {
    identifier: '',
    title: '',
    description: '',
    priority: 2,
    module: '',
    ownerId: null,
    plannedVersion: '',
    links: [],
    attachments: []
  }
  showCreateItemDialog.value = true
}

const addLink = () => {
  if (!itemForm.value.links) {
    itemForm.value.links = []
  }
  itemForm.value.links.push({
    linkType: 'implements',
    targetType: 'task',
    targetId: null
  })
}

const removeLink = (index) => {
  itemForm.value.links.splice(index, 1)
}

const addEditLink = () => {
  if (!editItemForm.value.links) {
    editItemForm.value.links = []
  }
  editItemForm.value.links.push({
    linkType: 'implements',
    targetType: 'task',
    targetId: null
  })
}

const removeEditLink = (index) => {
  editItemForm.value.links.splice(index, 1)
}

const handleAttachmentUpload = (results) => {
  console.log('Attachments uploaded:', results)
}

const getLinkTypeText = (linkType) => {
  const textMap = {
    'implements': '实现',
    'verifies': '验证',
    'affects': '影响',
    'related': '相关'
  }
  return textMap[linkType] || linkType
}

const getLinkTypeTag = (linkType) => {
  const tagMap = {
    'implements': 'success',
    'verifies': 'primary',
    'affects': 'warning',
    'related': 'info'
  }
  return tagMap[linkType] || 'info'
}

const fetchDocument = async () => {
  loading.value = true
  try {
    const response = await api.get(`/requirement-documents/${docId.value}`)
    if (response.success) {
      document.value = response.document
      items.value = response.document.items || []

      editForm.value = {
        name: document.value.name,
        docType: document.value.doc_type,
        description: document.value.description || ''
      }
    }
  } catch (error) {
    console.error('获取文档详情失败:', error)
    ElMessage.error('获取文档详情失败')
  } finally {
    loading.value = false
  }
}

const fetchVersions = async () => {
  try {
    const response = await api.get(`/requirement-documents/${docId.value}/versions`)
    if (response.success) {
      versions.value = response.versions || []
      if (versions.value.length >= 2) {
        compareVersion1.value = versions.value[versions.value.length - 1]?.version
        compareVersion2.value = versions.value[versions.value.length - 2]?.version
      }
    }
  } catch (error) {
    console.error('获取版本历史失败:', error)
  }
}

const fetchProjectMembers = async () => {
  try {
    // 优先从路由参数获取 projectId，如果没有则从文档详情获取
    const pid = projectId.value || document.value?.project_id
    if (!pid) {
      return
    }
    const response = await api.get(`/projects/${pid}`)
    if (response.project && response.project.members) {
      projectMembers.value = response.project.members.map(m => m.user || m)
    }
  } catch (error) {
    console.error('获取项目成员失败:', error)
  }
}

const fetchProjectDocuments = async () => {
  try {
    // 优先从路由参数获取 projectId，如果没有则从文档详情获取
    const pid = projectId.value || document.value?.project_id
    if (!pid) {
      return
    }
    const response = await api.get(`/projects/${pid}/requirement-documents`)
    if (response.success) {
      projectDocuments.value = response.documents || []
    }
  } catch (error) {
    console.error('获取项目文档失败:', error)
  }
}

const handleUpdate = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
    updating.value = true

    const data = {
      name: editForm.value.name,
      doc_type: editForm.value.docType,
      description: editForm.value.description
    }

    const response = await api.put(`/requirement-documents/${docId.value}`, data)
    if (response.success) {
      ElMessage.success('文档更新成功')
      showEditDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.error || '更新失败')
  } finally {
    updating.value = false
  }
}

const handleChangeStatus = async (status) => {
  try {
    const response = await api.post(`/requirement-documents/${docId.value}/change-status`, { status })
    if (response.success) {
      ElMessage.success('状态变更成功')
      fetchDocument()
    }
  } catch (error) {
    console.error('状态变更失败:', error)
    ElMessage.error(error.response?.data?.error || '状态变更失败')
  }
}

const handleCreateItem = async () => {
  if (!itemFormRef.value) return
  
  try {
    await itemFormRef.value.validate()
    creatingItem.value = true
    
    const data = {
      identifier: itemForm.value.identifier || `REQ-${items.value.length + 1}`,
      title: itemForm.value.title,
      description: itemForm.value.description,
      priority: itemForm.value.priority,
      module: itemForm.value.module,
      owner_id: itemForm.value.ownerId,
      planned_version: itemForm.value.plannedVersion
    }
    
    const response = await api.post(`/requirement-documents/${docId.value}/items`, data)
    if (response.success) {
      const newItem = response.item || response
      
      if (itemForm.value.links && itemForm.value.links.length > 0) {
        for (const link of itemForm.value.links) {
          if (link.targetId) {
            await api.post('/requirement-links', {
              requirement_id: newItem.id,
              target_type: link.targetType,
              target_id: link.targetId,
              link_type: link.linkType
            })
          }
        }
      }

      if (createAttachmentRef.value) {
        await createAttachmentRef.value.upload()
      }
      
      ElMessage.success('需求条目创建成功')
      showCreateItemDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('创建失败:', error)
    ElMessage.error(error.response?.data?.error || '创建失败')
  } finally {
    creatingItem.value = false
  }
}

const handleUpdateItem = async () => {
  if (!editItemFormRef.value) return
  
  try {
    await editItemFormRef.value.validate()
    updatingItem.value = true
    
    const data = {
      title: editItemForm.value.title,
      description: editItemForm.value.description,
      priority: editItemForm.value.priority,
      status: editItemForm.value.status,
      owner_id: editItemForm.value.ownerId,
      module: editItemForm.value.module,
      planned_version: editItemForm.value.plannedVersion,
      actual_version: editItemForm.value.actualVersion
    }
    
    const response = await api.put(`/requirement-items/${editItemForm.value.id}`, data)
    if (response.success) {
      if (editItemForm.value.links && editItemForm.value.links.length > 0) {
        for (const link of editItemForm.value.links) {
          if (link.targetId && !link.id) {
            await api.post('/requirement-links', {
              requirement_id: editItemForm.value.id,
              target_type: link.targetType,
              target_id: link.targetId,
              link_type: link.linkType
            })
          }
        }
      }

      if (editAttachmentRef.value) {
        await editAttachmentRef.value.upload()
      }
      
      ElMessage.success('需求条目更新成功')
      showEditItemDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.error || '更新失败')
  } finally {
    updatingItem.value = false
  }
}

const handleDeleteItem = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求条目 "${item.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await api.delete(`/requirement-items/${item.id}`)
    if (response.success) {
      ElMessage.success('删除成功')
      fetchDocument()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

const handleItemCommand = (command, item) => {
  selectedItem.value = item
  if (command === 'edit') {
    editItemForm.value = {
      id: item.id,
      title: item.title,
      description: item.description || '',
      priority: item.priority || 2,
      status: item.status,
      ownerId: item.owner_id,
      module: item.module || '',
      plannedVersion: item.planned_version || '',
      actualVersion: item.actual_version || '',
      links: item.links || [],
      attachments: item.attachments || []
    }
    showEditItemDialog.value = true
  } else if (command === 'delete') {
    handleDeleteItem(item)
  } else if (command === 'status') {
    ElMessageBox.prompt('请选择新的状态', '变更状态', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'select',
      inputOptions: {
        'pending_review': '待评审',
        'reviewed': '已评审',
        'approved': '已批准',
        'in_progress': '开发中',
        'completed': '已完成',
        'verified': '已验证'
      }
    }).then(({ value }) => {
      handleChangeItemStatus(item, value)
    }).catch(() => {})
  } else if (command === 'copy') {
    copyMoveAction.value = 'copy'
    copyMoveForm.value.targetDocId = docId.value
    showCopyMoveDialog.value = true
  } else if (command === 'move') {
    copyMoveAction.value = 'move'
    copyMoveForm.value.targetDocId = null
    showCopyMoveDialog.value = true
  } else if (command === 'history') {
    fetchItemHistory(item)
  } else if (command === 'impact') {
    fetchImpactAnalysis(item)
  } else if (command === 'review') {
    itemReviewForm.value = {
      conclusion: 'approved',
      comment: ''
    }
    showItemReviewDialog.value = true
  }
}

const handleChangeItemStatus = async (item, newStatus) => {
  try {
    const response = await api.post(`/requirement-items/${item.id}/change-status`, { status: newStatus })
    if (response.success) {
      ElMessage.success('状态变更成功')
      fetchDocument()
    }
  } catch (error) {
    console.error('状态变更失败:', error)
    ElMessage.error(error.response?.data?.error || '状态变更失败')
  }
}

const handleCopyMove = async () => {
  if (!copyMoveFormRef.value) return

  try {
    await copyMoveFormRef.value.validate()
    submittingCopyMove.value = true

    const data = {
      target_doc_id: copyMoveForm.value.targetDocId
    }

    let response
    if (copyMoveAction.value === 'copy') {
      response = await api.post(`/requirement-items/${selectedItem.value.id}/copy`, data)
    } else {
      response = await api.post(`/requirement-items/${selectedItem.value.id}/move`, data)
    }

    if (response.success) {
      ElMessage.success(copyMoveAction.value === 'copy' ? '复制成功' : '移动成功')
      showCopyMoveDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    submittingCopyMove.value = false
  }
}

const fetchItemHistory = async (item) => {
  try {
    const response = await api.get(`/requirement-items/${item.id}/history`)
    if (response.success) {
      itemHistory.value = response.history || []
      showHistoryDialog.value = true
    }
  } catch (error) {
    console.error('获取历史失败:', error)
    ElMessage.error('获取变更历史失败')
  }
}

const fetchImpactAnalysis = async (item) => {
  try {
    const response = await api.get(`/requirement-items/${item.id}/impact-analysis`)
    if (response.success) {
      impactAnalysis.value = response
      showImpactDialog.value = true
    }
  } catch (error) {
    console.error('获取影响分析失败:', error)
    ElMessage.error('获取影响分析失败')
  }
}

const handleItemReview = async () => {
  if (!itemReviewFormRef.value) return

  try {
    await itemReviewFormRef.value.validate()
    submittingItemReview.value = true

    const data = {
      conclusion: itemReviewForm.value.conclusion,
      comment: itemReviewForm.value.comment
    }

    const response = await api.post(`/requirement-items/${selectedItem.value.id}/review`, data)
    if (response.success) {
      ElMessage.success('评审提交成功')
      showItemReviewDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('评审提交失败:', error)
    ElMessage.error(error.response?.data?.error || '评审提交失败')
  } finally {
    submittingItemReview.value = false
  }
}

const fetchVersionDiff = async () => {
  if (!compareVersion1.value || !compareVersion2.value) {
    ElMessage.warning('请选择两个版本进行对比')
    return
  }

  try {
    const response = await api.get(`/requirement-documents/${docId.value}/compare-versions`, {
      params: {
        v1: compareVersion1.value,
        v2: compareVersion2.value
      }
    })
    if (response.success) {
      versionDiff.value = response.differences
    }
  } catch (error) {
    console.error('版本对比失败:', error)
    ElMessage.error('版本对比失败')
  }
}

const handleRollback = async (versionNum) => {
  try {
    await ElMessageBox.confirm(
      `确定要回滚到版本 ${versionNum} 吗？这将创建一个新版本，内容与指定版本相同。`,
      '确认回滚',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await api.post(`/requirement-documents/${docId.value}/rollback/${versionNum}`)
    if (response.success) {
      ElMessage.success('回滚成功')
      showVersionHistory.value = false
      fetchDocument()
      fetchVersions()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('回滚失败:', error)
      ElMessage.error(error.response?.data?.error || '回滚失败')
    }
  }
}

const handleInitiateReview = async () => {
  if (!reviewFormRef.value) return

  try {
    await reviewFormRef.value.validate()
    submittingReview.value = true

    const data = {
      reviewers: reviewForm.value.reviewers,
      deadline: reviewForm.value.deadline,
      review_type: reviewForm.value.reviewType,
      scope: reviewForm.value.scope,
      comment: reviewForm.value.comment
    }

    const response = await api.post(`/requirement-documents/${docId.value}/review`, data)
    if (response.success) {
      ElMessage.success('评审已发起')
      showReviewDialog.value = false
      fetchDocument()
    }
  } catch (error) {
    console.error('发起评审失败:', error)
    ElMessage.error(error.response?.data?.error || '发起评审失败')
  } finally {
    submittingReview.value = false
  }
}

const handleExport = async (format) => {
  try {
    const response = await api.get(`/requirement-documents/${docId.value}/export`, {
      params: { format },
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    const filename = `${document.value.name}.${format === 'markdown' ? 'md' : format}`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const goToImpactAnalysis = () => {
  if (selectedItem.value) {
    fetchImpactAnalysis(selectedItem.value)
  }
}

const handleCreateVersion = async () => {
  try {
    const { value } = await ElMessageBox.prompt(
      '请输入版本变更说明',
      '创建新版本',
      {
        confirmButtonText: '创建',
        cancelButtonText: '取消',
        inputPlaceholder: '简要描述本次变更内容'
      }
    )
    
    const response = await api.post(`/requirement-documents/${docId.value}/create-version`, {
      change_summary: value
    })
    if (response.success) {
      ElMessage.success('新版本创建成功')
      fetchVersions()
      fetchDocument()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('创建版本失败:', error)
      ElMessage.error(error.response?.data?.error || '创建版本失败')
    }
  }
}

const toggleExpand = (itemId) => {
  const index = expandedItems.value.indexOf(itemId)
  if (index > -1) {
    expandedItems.value.splice(index, 1)
  } else {
    expandedItems.value.push(itemId)
  }
}

const goBack = () => {
  if (canGoBack.value && window.history.length > 1) {
    router.go(-1)
  } else if (projectId.value) {
    router.push(`/projects/${projectId.value}/requirements`)
  } else {
    router.push('/requirements')
  }
}

const canGoBack = ref(false)

const goToTraceMatrix = () => {
  if (projectId.value && docId.value) {
    router.push(`/projects/${projectId.value}/requirements/${docId.value}/trace-matrix`)
  }
}

const getStatusType = (status) => {
  const typeMap = {
    'draft': 'info',
    'reviewing': 'warning',
    'approved': 'success',
    'deprecated': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'draft': '草稿',
    'reviewing': '评审中',
    'approved': '已批准',
    'deprecated': '已废弃'
  }
  return textMap[status] || status
}

const getItemStatusType = (status) => {
  const typeMap = {
    'pending_review': 'info',
    'reviewed': 'warning',
    'approved': 'success',
    'in_progress': 'primary',
    'completed': 'success',
    'verified': 'success'
  }
  return typeMap[status] || 'info'
}

const getItemStatusText = (status) => {
  const textMap = {
    'pending_review': '待评审',
    'reviewed': '已评审',
    'approved': '已批准',
    'in_progress': '开发中',
    'completed': '已完成',
    'verified': '已验证'
  }
  return textMap[status] || status
}

const getPriorityType = (priority) => {
  const typeMap = {
    1: 'info',
    2: 'warning',
    3: 'danger'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    1: '低',
    2: '中',
    3: '高'
  }
  return textMap[priority] || priority
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(async () => {
  canGoBack.value = window.history.length > 1
  await fetchDocument()
  // 在获取文档详情后再获取项目成员和文档列表（用于处理独立路由 /requirements/:id）
  fetchProjectMembers()
  fetchProjectDocuments()
  fetchVersions()

  const itemId = route.query.itemId
  if (itemId) {
    setTimeout(() => {
      const id = parseInt(itemId)
      if (!expandedItems.value.includes(id)) {
        expandedItems.value.push(id)
      }
      nextTick(() => {
        const element = document.querySelector(`[data-item-id="${id}"]`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      })
    }, 500)
  }
})
</script>

<style scoped>
.requirement-doc-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.doc-info h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.doc-tags {
  display: flex;
  gap: 8px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.description-card {
  margin-bottom: 20px;
}

.description-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.items-card {
  margin-bottom: 20px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-row {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.item-row:hover {
  border-color: #409eff;
}

.item-row.expanded {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.item-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  background-color: #fafafa;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-icon {
  transition: transform 0.3s;
  color: #909399;
}

.expanded .expand-icon {
  transform: rotate(90deg);
}

.item-identifier {
  font-family: monospace;
  font-weight: 600;
  color: #409eff;
  background-color: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.item-title {
  font-weight: 500;
  color: #303133;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.item-actions .el-button {
  padding: 4px;
}

.item-actions .el-icon {
  font-size: 16px;
}

.item-owner,
.item-comments {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.item-detail {
  padding: 0 20px 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
}

.detail-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  color: #909399;
  font-size: 12px;
}

.detail-item span {
  color: #303133;
  font-size: 14px;
}

.comments-section {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.comments-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.version-creator {
  color: #909399;
  font-size: 13px;
  margin-top: 8px;
}

.diff-result {
  margin-top: 20px;
}

.diff-section {
  margin: 16px 0;
}

.diff-section h4 {
  margin: 8px 0;
  color: #303133;
}

.diff-item {
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 4px;
}

.diff-added {
  background-color: #f0f9eb;
  border-left: 3px solid #67c23a;
}

.diff-removed {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.diff-modified {
  background-color: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.item-dialog .el-dialog__body {
  padding-top: 20px;
}

.links-editor {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.link-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.link-row:last-child {
  margin-bottom: 0;
}

.detail-content img {
  max-width: 100%;
  height: auto;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.link-target {
  color: #606266;
  font-size: 14px;
}

.links-editor .el-divider {
  margin: 16px 0 12px 0;
}

.item-dialog .el-divider--horizontal {
  margin: 16px 0;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .requirement-doc-detail {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 8px 12px;
  }

  .description-card,
  .requirements-card {
    margin-bottom: 16px;
  }

  .description-content {
    font-size: 13px;
  }

  .requirements-list {
    gap: 12px;
  }

  .requirement-item {
    padding: 12px;
  }

  .requirement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 8px;
  }

  .requirement-id {
    font-size: 12px;
  }

  .requirement-name {
    font-size: 14px;
  }

  .requirement-description {
    font-size: 12px;
  }

  .requirement-meta {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 11px;
  }

  .el-dialog {
    width: 95% !important;
    margin: 10px auto !important;
    max-height: 90vh !important;
  }

  .el-dialog__header,
  .el-dialog__body,
  .el-dialog__footer {
    padding: 12px !important;
  }

  .el-dialog__title {
    font-size: 16px !important;
  }

  .el-form-item {
    margin-bottom: 12px;
  }

  .el-form-item__label {
    font-size: 12px;
  }

  .links-editor .link-item {
    flex-direction: column;
    gap: 8px;
  }

  .link-type,
  .link-target {
    font-size: 12px;
  }
}

@media screen and (max-width: 480px) {
  .requirement-doc-detail {
    padding: 8px;
  }

  .page-header h2 {
    font-size: 16px;
  }

  .requirement-name {
    font-size: 13px;
  }

  .requirement-description {
    font-size: 11px;
  }

  .requirement-meta {
    font-size: 10px;
  }
}
</style>
