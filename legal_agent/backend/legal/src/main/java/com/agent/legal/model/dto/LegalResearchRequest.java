package com.agent.legal.model.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class LegalResearchRequest {
    @NotBlank
    private String query;
}
