package com.agent.legal.service;

import com.agent.legal.mapper.TaskReminderMapper;
import com.agent.legal.model.dto.ReminderRequest;
import com.agent.legal.model.entity.SysUser;
import com.agent.legal.model.entity.TaskReminder;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ReminderService {
    private final TaskReminderMapper taskReminderMapper;
    private final AuditService auditService;

    public TaskReminder createReminder(ReminderRequest request, SysUser currentUser) {
        TaskReminder reminder = new TaskReminder();
        reminder.setRelatedType(TaskReminder.RelatedType.valueOf(request.getRelatedType()));
        reminder.setRelatedId(request.getRelatedId());
        reminder.setTitle(request.getTitle());
        reminder.setDueDate(request.getDueDate());
        reminder.setAssignedTo(currentUser.getUserId());
        TaskReminder saved = taskReminderMapper.save(reminder);
        auditService.log(currentUser.getUserId(), "REMINDER_CREATE", "提醒ID:" + saved.getTaskId());
        return saved;
    }

    public List<TaskReminder> getUnfinished(Integer userId) {
        return taskReminderMapper.findByAssignedToAndIsCompletedFalse(userId);
    }

    public void markCompleted(Integer taskId, SysUser currentUser) {
        TaskReminder reminder = taskReminderMapper.findById(taskId)
                .orElseThrow(() -> new RuntimeException("提醒不存在"));
        if (!reminder.getAssignedTo().equals(currentUser.getUserId()) && !"admin".equals(currentUser.getRole().name())) {
            throw new RuntimeException("无权操作");
        }
        taskReminderMapper.markCompleted(taskId);
        auditService.log(currentUser.getUserId(), "REMINDER_COMPLETE", "提醒ID:" + taskId);
    }
}
