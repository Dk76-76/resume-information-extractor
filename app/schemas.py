"""Pydantic schemas for Resume Information Extraction System."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    """Represents an education entry."""
    degree: str = Field(..., description="Degree or credential (e.g. B.Tech, M.S., High School)")
    institution: Optional[str] = Field(default=None, description="College, University or School name")
    year: Optional[str] = Field(default=None, description="Graduation year or date range")
    university: Optional[str] = Field(default=None, description="University name if separate from college")
    cgpa: Optional[str] = Field(default=None, description="CGPA or grade")
    percentage: Optional[str] = Field(default=None, description="Percentage score")


class ExperienceItem(BaseModel):
    """Represents a work experience entry."""
    title: str = Field(..., description="Job title or role (e.g. Software Engineer, Intern)")
    company: Optional[str] = Field(default=None, description="Company or Organization name")
    duration: Optional[str] = Field(default=None, description="Tenure or employment period")


class ResumeData(BaseModel):
    """Structured resume data model."""
    name: Optional[str] = Field(default=None, description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Candidate's email address")
    phone: Optional[str] = Field(default=None, description="Candidate's contact phone number")
    skills: List[str] = Field(default_factory=list, description="List of detected technical and professional skills")
    education: List[EducationItem] = Field(default_factory=list, description="Education history")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience history")
    linkedin: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="GitHub profile URL")


class ExtractionResponse(BaseModel):
    """API response model for extraction requests."""
    success: bool
    filename: str
    message: str
    data: ResumeData
